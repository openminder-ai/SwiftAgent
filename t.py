import arxiv, asyncio

import warnings

warnings.filterwarnings("ignore")

from swiftagent import SwiftAgent
from swiftagent.memory.semantic import SemanticMemory
from swiftagent.prebuilt.storage.chroma import ChromaDatabase

ChromaDatabase("./chroma_db").clear()
