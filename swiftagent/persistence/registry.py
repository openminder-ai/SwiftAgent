import os
import json
import cloudpickle  # or dill
from pathlib import Path

from swiftagent.constants import CACHE_DIR
from swiftagent.memory.base import MemoryItem, MemoryItemType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swiftagent.application import SwiftAgent


def ensure_dir_exists(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


class AgentRegistry:
    @staticmethod
    def save_agent_profile(agent: "SwiftAgent"):
        if not agent.persist_path:
            return

        ensure_dir_exists(agent.persist_path)

        # 1) Save the basic agent profile
        profile = {
            "name": agent.name,
            "description": agent.description,
            "instruction": agent.instruction,
            "llm_name": agent.llm_name,
            "episodic_memory": bool(
                agent.working_memory and agent.long_term_memory
            ),
            # Add custom
            "auto_save": agent.auto_save,
            "auto_load": agent.auto_load,
            "verbose": agent.verbose,
        }
        with open(
            os.path.join(agent.persist_path, "agent_profile.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(profile, f, indent=2)

        # 2) Save actions metadata
        actions_meta = []
        actions_dir = os.path.join(agent.persist_path, "actions")
        ensure_dir_exists(actions_dir)

        for action_name, action_obj in agent._actions.items():
            # a) Pickle the function object itself
            pkl_path = os.path.join(actions_dir, f"{action_name}.pkl")
            with open(pkl_path, "wb") as f_pk:
                cloudpickle.dump(action_obj.func, f_pk)

            # b) Save the metadata in a central JSON
            actions_meta.append(
                {
                    "name": action_name,
                    "description": action_obj.description,
                    "params": action_obj.params,
                    "strict": action_obj.strict,
                    # We do not store "source_code" now—just a reference to .pkl
                    "pickle_path": f"actions/{action_name}.pkl",
                }
            )

        # Write out the consolidated actions.json
        with open(
            os.path.join(agent.persist_path, "actions.json"),
            "w",
            encoding="utf-8",
        ) as f_act:
            json.dump(actions_meta, f_act, indent=2)

        # 3) Save memory config
        mem_config = {}
        if agent.working_memory:
            # new approach: single unified list
            mem_config["working_memory"] = {
                "max_items": agent.working_memory.max_items,
            }

            # Gather data from the unified list
            wm_history_data = []
            for m in agent.working_memory.history:
                wm_history_data.append(
                    {
                        "item_type": m.item_type.value,
                        "content": m.content,
                        "timestamp": m.timestamp,
                    }
                )

            mem_config["working_memory_data"] = {"history": wm_history_data}

        if agent.long_term_memory:
            mem_config["long_term_memory"] = {
                "name": agent.long_term_memory.name,
                "persist_directory": agent.long_term_memory.collection.path,
            }
        if agent.semantic_memories:
            sem_dict = {}
            for sm_name, sm_obj in agent.semantic_memories.items():
                col_name = sm_obj.container_collection.name
                # In your code, you might need to carefully check if the underlying DB is a Chroma client
                # and get the directory differently. Shown below is typical if you used the ChromaDatabase wrapper.
                # If it doesn't apply, you can skip or adapt.
                try:
                    path_ = (
                        sm_obj.container_collection._collection._client.settings.chroma_db_impl._db_dir
                    )
                except:
                    path_ = str(CACHE_DIR / "chroma_db")

                sem_dict[sm_name] = {
                    "name": sm_obj.name,
                    "collection_name": col_name,
                    "persist_directory": path_,
                }
            mem_config["semantic_memories"] = sem_dict

        with open(
            os.path.join(agent.persist_path, "memory_config.json"),
            "w",
            encoding="utf-8",
        ) as f_mem:
            json.dump(mem_config, f_mem, indent=2)

    @staticmethod
    def load_agent_profile(agent: "SwiftAgent"):
        if not agent.persist_path:
            return

        profile_path = os.path.join(agent.persist_path, "agent_profile.json")
        actions_path = os.path.join(agent.persist_path, "actions.json")
        mem_config_path = os.path.join(agent.persist_path, "memory_config.json")

        if not os.path.exists(profile_path):
            return

        # 1) Load profile
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        agent.name = data["name"]
        agent.description = data["description"]
        agent.instruction = data["instruction"]
        agent.llm_name = data["llm_name"]
        episodic_memory = data.get("episodic_memory", False)

        if "auto_save" in data:
            agent.auto_save = data["auto_save"]
        if "auto_load" in data:
            agent.auto_load = data["auto_load"]
        if "verbose" in data:
            agent.verbose = data["verbose"]

        if episodic_memory:
            from swiftagent.reasoning.salient import SalientMemoryReasoning

            agent.reasoning = SalientMemoryReasoning(
                name=agent.name,
                instructions=agent.instruction,
                working_memory=agent.working_memory,
                long_term_memory=agent.long_term_memory,
            )

        # 2) Load actions
        if os.path.exists(actions_path):
            with open(actions_path, "r", encoding="utf-8") as f_act:
                actions_meta = json.load(f_act)

            import cloudpickle
            from swiftagent.actions.base import Action

            for meta in actions_meta:
                a_name = meta["name"]
                a_desc = meta["description"]
                a_params = meta["params"]
                a_strict = meta["strict"]
                pkl_path = meta["pickle_path"]

                full_path = os.path.join(agent.persist_path, pkl_path)
                if not os.path.exists(full_path):
                    print(f"Action pickle not found: {full_path}")
                    continue

                with open(full_path, "rb") as f_pk:
                    loaded_func = cloudpickle.load(f_pk)

                action_obj = Action(
                    func=loaded_func,
                    name=a_name,
                    description=a_desc,
                    params=a_params,
                    strict=a_strict,
                )
                agent.add_action(a_name, action_obj)

        # 3) Load memory config
        if os.path.exists(mem_config_path):
            with open(mem_config_path, "r", encoding="utf-8") as f_mem:
                memconf = json.load(f_mem)

            if "working_memory" in memconf:
                from swiftagent.memory.working import WorkingMemory

                wconf = memconf["working_memory"]

                # Create a new WorkingMemory with the new unified approach
                agent._create_or_replace_working_memory(
                    max_items=wconf.get("max_items", 15),
                )

                # Now fill in the history from working_memory_data
                data_ = memconf.get("working_memory_data", {})
                if "history" in data_:
                    for item_data in data_["history"]:
                        # For backward-compat, if something was stored differently,
                        # you could do an if-check. We'll assume correct shape:
                        mtype_str = item_data.get("item_type", "TEXT")
                        mtype = MemoryItemType(mtype_str)
                        content = item_data.get("content", "")
                        timestamp = item_data.get("timestamp", "")

                        mem_item = MemoryItem(
                            item_type=mtype,
                            content=content,
                            timestamp=timestamp,
                        )
                        agent.working_memory.history.append(mem_item)

            if "long_term_memory" in memconf:
                from swiftagent.memory.long_term import LongTermMemory

                ltm_ = memconf["long_term_memory"]
                agent._create_or_replace_long_term_memory(
                    name=ltm_["name"],
                )

            if "semantic_memories" in memconf:
                from swiftagent.prebuilt.storage.chroma import ChromaDatabase
                from swiftagent.memory.semantic import SemanticMemory

                for sm_name, sm_data in memconf["semantic_memories"].items():
                    path_ = sm_data.get(
                        "persist_directory", str(CACHE_DIR / "chroma_db")
                    )
                    col_name = sm_data["collection_name"]
                    db = ChromaDatabase(persist_directory=path_)
                    col = db.get_or_create_collection(name=col_name)
                    sm = SemanticMemory(name=sm_name, container_collection=col)
                    agent.add_semantic_memory_section(sm)
