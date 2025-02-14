from markitdown import MarkItDown

md = MarkItDown()


def read_files(filenames: list[str]):
    md = MarkItDown()

    return "\n".join(
        [
            f"# {filename} \n {md.convert(filename).text_content} \n"
            for filename in filenames
        ]
    )


print(read_files("/Users/balaji/Downloads/Shareholder-2 (1).pdf"))
