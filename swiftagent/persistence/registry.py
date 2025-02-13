import os
import json
import cloudpickle  # or dill
from pathlib import Path

from swiftagent.memory.base import MemoryItem, MemoryItemType


def ensure_dir_exists(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


class AgentRegistry:
    @staticmethod
    def save_agent_profile(agent):
        if not agent.persist_path:
            return

        ensure_dir_exists(agent.persist_path)

        # 1) Save the basic agent profile
        profile = {
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

        # 3) Save memory config (like before)
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
            sem_dict = {}
            for sm_name, sm_obj in agent.semantic_memories.items():
                sem_dict[sm_name] = {
                    "name": sm_obj.name,
                    "collection_name": sm_obj.container_collection.name,
                    "persist_directory": (
                        sm_obj.container_collection._collection._client.settings.chroma_db_impl._db_dir
                        if hasattr(
                            sm_obj.container_collection._collection._client,
                            "settings",
                        )
                        else None
                    ),
                }
            mem_config["semantic_memories"] = sem_dict

        with open(
            os.path.join(agent.persist_path, "memory_config.json"),
            "w",
            encoding="utf-8",
        ) as f_mem:
            json.dump(mem_config, f_mem, indent=2)

    @staticmethod
    def load_agent_profile(agent):
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
        enable_salient = data.get("enable_salient_memory", False)

        # 2) Load each action from .pkl
        if os.path.exists(actions_path):
            with open(actions_path, "r", encoding="utf-8") as f_act:
                actions_meta = json.load(f_act)

            for meta in actions_meta:
                a_name = meta["name"]
                a_desc = meta["description"]
                a_params = meta["params"]
                a_strict = meta["strict"]
                pkl_path = meta["pickle_path"]  # e.g. "actions/get_weather.pkl"

                full_path = os.path.join(agent.persist_path, pkl_path)
                if not os.path.exists(full_path):
                    print(f"Action pickle not found: {full_path}")
                    continue

                # Un-pickle
                import cloudpickle

                with open(full_path, "rb") as f_pk:
                    loaded_func = cloudpickle.load(f_pk)

                # Now we create a new Action wrapper with the loaded function
                from swiftagent.actions.base import Action
                from swiftagent.actions.base import Action

                action_obj = Action(
                    func=loaded_func,
                    name=a_name,
                    description=a_desc,
                    params=a_params,
                    strict=a_strict,
                )
                # Attach it
                agent.add_action(a_name, action_obj)

        # 3) Load memory config (like before)
        if os.path.exists(mem_config_path):
            with open(mem_config_path, "r", encoding="utf-8") as f_mem:
                memconf = json.load(f_mem)

            if "working_memory" in memconf:
                wconf = memconf["working_memory"]
                agent._create_or_replace_working_memory(
                    max_text_items=wconf.get("max_text_items", 10),
                    max_action_items=wconf.get("max_action_items", 10),
                )
                data_ = memconf.get("working_memory_data", {})
                text_history = data_.get("text_history", [])
                action_history = data_.get("action_history", [])
                for t in text_history:
                    from swiftagent.memory.base import (
                        MemoryItem,
                        MemoryItemType,
                    )

                    item = MemoryItem(
                        MemoryItemType(t["item_type"]), t["content"]
                    )
                    agent.working_memory.text_history.append(item)
                for a in action_history:
                    from swiftagent.memory.base import (
                        MemoryItem,
                        MemoryItemType,
                    )

                    item = MemoryItem(
                        MemoryItemType(a["item_type"]), a["content"]
                    )
                    agent.working_memory.action_history.append(item)

            if "long_term_memory" in memconf:
                ltm_ = memconf["long_term_memory"]
                agent._create_or_replace_long_term_memory(
                    name=ltm_["name"],
                    persist_directory=ltm_["persist_directory"],
                )

            if "semantic_memories" in memconf:
                from swiftagent.prebuilt.storage.chroma import ChromaDatabase
                from swiftagent.memory.semantic import SemanticMemory

                for sm_name, sm_data in memconf["semantic_memories"].items():
                    path_ = sm_data.get("persist_directory", "./chroma_db")
                    col_name = sm_data["collection_name"]
                    db = ChromaDatabase(persist_directory=path_)
                    col = db.get_or_create_collection(name=col_name)
                    sm = SemanticMemory(name=sm_name, container_collection=col)
                    agent.add_semantic_memory_section(sm)
