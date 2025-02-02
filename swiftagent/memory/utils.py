from langchain_text_splitters import RecursiveCharacterTextSplitter

_text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=4000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)


def text_splitter(text: str) -> list[str]:
    texts = _text_splitter.create_documents([text])

    return [text.page_content for text in texts]
