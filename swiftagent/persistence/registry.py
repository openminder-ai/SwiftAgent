import os
import json
import inspect
import textwrap
from typing import Optional, Dict, Any
from pathlib import Path
import re

# from swiftagent.application.base import SwiftAgent

from swiftagent.actions.wrapper import action as standalone_action_decorator


from swiftagent.memory.base import MemoryItem, MemoryItemType


def ensure_dir_exists(dir_path: str) -> None:
    """Helper to create the directory if it doesn't exist."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


class AgentRegistry:
    """
    A simple registry that can persist and load SwiftAgent 'profiles' to/from disk.

    Each Agent has a unique 'persist_path' directory where we store:
      - agent_profile.json (name, description, instructions, etc.)
      - actions.json (list of (action_name, code_string, metadata))
      - memory_config.json (where we store the memory type + config)
      - other artifacts (like the Chroma DB for LTM in a subfolder)
    """

    @staticmethod
    def save_agent_profile(agent: Any) -> None:
        if not agent.persist_path:
            return  # no-op if no persist_path

        ensure_dir_exists(agent.persist_path)

        # 1) Dump agent_profile.json
        profile_data = {
            "name": agent.name,
            "description": agent.description,
            "instruction": agent.instruction,
            "llm_name": agent.llm_name,
            "enable_salient_memory": bool(
                agent.working_memory and agent.long_term_memory
            ),
        }
        with open(
            os.path.join(agent.persist_path, "agent_profile.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(profile_data, f, indent=2)

        # 2) Save actions
        actions_list = []
        for action_name, action_obj in agent._actions.items():
            try:
                src_lines, _ = inspect.getsourcelines(action_obj.func)
                # Combine them into a single string
                src_code = "".join(src_lines)
            except Exception:
                # If we can’t read the source for some reason, store a dummy
                src_code = "# Could not retrieve source code.\n"

            # -- NEW STEP: Transform any '@agent.action(...)' lines to '@action(...)' --
            # 1) Insert 'from swiftagent.actions.wrapper import action' at the top, if not present
            #    but only if we actually detect an @...action( in the snippet
            insert_import = False
            if re.search(r"@[a-zA-Z_]\w*\.action\s*\(", src_code):
                insert_import = True

            # 2) Replace all lines with '@X.action(...)' => '@action(...)'
            def replace_agent_dot_action(match):
                # match.group(1) is the 'X' in '@X.action'
                # match.group(2) is everything inside the parentheses
                args = match.group(2)
                # Rebuild as '@action(...)'
                return f"@action({args})"

            # Example pattern:  @agent.action(...) or @my_agent.action(...)
            pattern = r"@([a-zA-Z_]\w*)\.action\s*\((.*?)\)"
            # Use DOTALL or something if you might have multiline
            cleaned_code = re.sub(
                pattern, replace_agent_dot_action, src_code, flags=re.DOTALL
            )

            if insert_import:
                # If the snippet doesn’t already have this import,
                # add it right at the top (unless there's a def line or docstring first).
                # We'll do something naive: just prepend the line if not present.
                if (
                    "from swiftagent.actions.wrapper import action"
                    not in cleaned_code
                ):
                    cleaned_code = (
                        "from swiftagent.actions.wrapper import action\n\n"
                        + cleaned_code
                    )

            # Dedent
            cleaned_code = textwrap.dedent(cleaned_code)

            actions_list.append(
                {
                    "name": action_name,
                    "description": action_obj.description,
                    "params": action_obj.params,
                    "strict": action_obj.strict,
                    # store the final, cleaned code
                    "source_code": cleaned_code,
                }
            )

        with open(
            os.path.join(agent.persist_path, "actions.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(actions_list, f, indent=2)

        # 3) Save memory config, etc. (same as your existing logic)
        mem_config = {}
        if agent.working_memory:
            mem_config["working_memory"] = {
                "max_text_items": agent.working_memory.max_text_items,
                "max_action_items": agent.working_memory.max_action_items,
            }
            mem_config["working_memory_data"] = {
                "text_history": [
                    {"item_type": m.item_type.value, "content": m.content}
                    for m in agent.working_memory.text_history
                ],
                "action_history": [
                    {"item_type": m.item_type.value, "content": m.content}
                    for m in agent.working_memory.action_history
                ],
            }
        if agent.long_term_memory:
            mem_config["long_term_memory"] = {
                "name": agent.long_term_memory.name,
                "persist_directory": agent.long_term_memory.db.persist_directory,
            }
        if agent.semantic_memories:
            semantic_info = {}
            for sm_name, sm_obj in agent.semantic_memories.items():
                # store info about each semantic memory
                path_ = None
                try:
                    path_ = (
                        sm_obj.container_collection._collection._client.settings.chroma_db_impl._db_dir
                    )
                except:
                    pass
                semantic_info[sm_name] = {
                    "name": sm_obj.name,
                    "collection_name": sm_obj.container_collection.name,
                    "persist_directory": path_,
                }
            mem_config["semantic_memories"] = semantic_info

        with open(
            os.path.join(agent.persist_path, "memory_config.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(mem_config, f, indent=2)

    @staticmethod
    def load_agent_profile(agent: Any) -> None:
        """
        Load the agent’s profile from disk, re-constructing actions, memory, etc.
        This modifies the given agent *in-place*.
        If some fields are already set, we will attempt to override them with the loaded data.
        """
        if not agent.persist_path:
            return  # nothing to load

        agent_profile_path = os.path.join(
            agent.persist_path, "agent_profile.json"
        )
        actions_path = os.path.join(agent.persist_path, "actions.json")
        memory_config_path = os.path.join(
            agent.persist_path, "memory_config.json"
        )

        # If no agent_profile.json, there's nothing to load
        if not os.path.exists(agent_profile_path):
            return

        # 1) Load basic profile
        with open(agent_profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)

        agent.name = profile_data["name"]
        agent.description = profile_data["description"]
        agent.instruction = profile_data["instruction"]
        agent.llm_name = profile_data["llm_name"]

        enable_salient_memory = profile_data["enable_salient_memory"]

        # 2) Load and reconstruct actions
        if os.path.exists(actions_path):
            with open(actions_path, "r", encoding="utf-8") as f:
                actions_list = json.load(f)

            for adef in actions_list:
                # Rebuild the function from source code
                # We'll create a local dictionary, exec the code, then find the function object
                # The action code could define multiple things, so we do a mini-namespace
                locls = {}
                try:
                    exec(adef["source_code"], {}, locls)
                except Exception as e:
                    # If there's an error, skip or store a dummy
                    print(f"Error re-constructing action '{adef['name']}': {e}")
                    continue

                # We try to find the function by same name
                # (If the user used a different function name or declared multiple, we guess.)
                fn = locls.get(adef["name"], None)
                if fn is None:
                    # fallback: if there's only one function in locls, let's use it
                    candidates = [v for k, v in locls.items() if callable(v)]
                    if len(candidates) == 1:
                        fn = candidates[0]

                # If we still don't have it, skip
                if fn is None:
                    print(
                        f"Could not find a function for action '{adef['name']}'. Skipping."
                    )
                    continue

                # Now wrap it as an Action using the same metadata
                # We'll do so by re-using the existing action() decorator:
                # But we must specify the same name, description, etc.
                # Then we add it to the agent
                new_action_decorator = standalone_action_decorator(
                    name=adef["name"],
                    description=adef["description"],
                    params=adef["params"],
                    strict=adef["strict"],
                )
                rebuilt_func = new_action_decorator(fn)
                agent.add_action(rebuilt_func)

        # 3) Load memory config
        if os.path.exists(memory_config_path):
            with open(memory_config_path, "r", encoding="utf-8") as f:
                mem_config = json.load(f)

            # Working memory rehydration:
            if "working_memory" in mem_config:
                wconf = mem_config["working_memory"]
                agent._create_or_replace_working_memory(
                    max_text_items=wconf.get("max_text_items", 10),
                    max_action_items=wconf.get("max_action_items", 10),
                )
                # Restore data
                wmdata = mem_config.get("working_memory_data", {})
                text_items = wmdata.get("text_history", [])
                action_items = wmdata.get("action_history", [])

                for ti in text_items:
                    item = MemoryItem(
                        item_type=MemoryItemType(ti["item_type"]),
                        content=ti["content"],
                    )
                    agent.working_memory.text_history.append(item)

                for ai in action_items:
                    item = MemoryItem(
                        item_type=MemoryItemType(ai["item_type"]),
                        content=ai["content"],
                    )
                    agent.working_memory.action_history.append(item)

            if "long_term_memory" in mem_config:
                ltm_conf = mem_config["long_term_memory"]
                # Replace the agent's LTM with a new one, using that path
                agent._create_or_replace_long_term_memory(
                    name=ltm_conf["name"],
                    persist_directory=ltm_conf["persist_directory"],
                )

            # semantic memories
            if "semantic_memories" in mem_config:
                # We'll rebuild each semantic memory
                from swiftagent.prebuilt.storage.chroma import ChromaDatabase
                from swiftagent.memory.semantic import SemanticMemory
                from swiftagent.core.storage import VectorCollection

                sem_conf = mem_config["semantic_memories"]
                for sm_name, sm_data in sem_conf.items():
                    # Re-create the Chroma DB with the stored location if we have it
                    # Then get or create the collection named sm_data["collection_name"]
                    path_ = sm_data.get("persist_directory") or "./chroma_db"
                    db = ChromaDatabase(persist_directory=path_)
                    col = db.get_or_create_collection(
                        name=sm_data["collection_name"]
                    )
                    sm = SemanticMemory(name=sm_name, container_collection=col)
                    agent.add_semantic_memory_section(sm)

        # If the user is meant to have 'enable_salient_memory' behavior, do so.
        # But if we've already constructed them from the config, it’s effectively done.
        # We won't forcibly re-initialize them if they're already set up.


#
# END OF AgentRegistry
#
