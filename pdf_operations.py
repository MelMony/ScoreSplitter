import PyPDF2
from pathlib import Path

def add_metadata(file, output_path, metadata):
    """Creates a new pdf by copying the contents of the supplied pdf and adding the supplied PDF standard metadata.

    Args:
        file (str): A file path representing the inputpdf file for which to add metadata
        output_path (str): A directory path representing the location to output the new pdf with metadata
        metadata (dict[str, str]): A dictionary of key/value pairs representing the metadata to add to the pdf. Keys must follow the PDF standard.
    """
    
    try:
        if Path(file).suffix != '.pdf':
            raise TypeError('Input file must be a pdf')
        
        with open(file, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            # Update metadata in the new PDF writer
            pdf_writer.add_metadata(metadata)

            # Copy all pages from the original PDF to the new PDF writer
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        # Create complete set with the new metadata
        title = metadata.get('/Title')
        output_path_pdf = f'{output_path}/{title} - Complete Set.pdf'
                
        with open(output_path_pdf, "wb") as output_pdf:
            pdf_writer.write(output_pdf)

        print("Complete set with metadata created.")

    except FileNotFoundError:
        print(f"File not found: {file}")
    except TypeError:
        print('File supplied is not of the .pdf format.')

def split_score_by_bookmarks(score_pdf, part_names, metadata, output_directory):
    """Splits the given pdf score by its bookmarks that correlate to the given part names. The generated parts will include the given metadata and be stored at the given output location.

    Args:
        score_pdf (str): A file path representing the pdf of the score to be split into parts. Must contain bookmarks (outlines).
        part_names (list[str]): A list of part names that correlate with the given bookmarks. The number of bookmarks and parts must match.
        metadata (dict[str,str]): A dictionary of key/value pairs representing the metadata to add to the pdf. Keys must follow the PDF standard.
        output_directory (str): A file path representing the output directory location to store the newly created files.
    """
    try:
        if Path(score_pdf).suffix != '.pdf':
            raise TypeError('Input file must be a pdf')
        
        with open(score_pdf, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            bookmarks = pdf_reader.outline
            if len(bookmarks) != len(part_names):
                raise ValueError(f"Mismatch between bookmark count ({len(bookmarks)}) and the supplied part names count ({len(part_names)})")

            # Loop through each bookmarked section
            for i in range(len(bookmarks)):
                print(f"Creating part {part_names[i]}")
                page_num_current_bookmark = pdf_reader.get_destination_page_number(
                    bookmarks[i]
                )
                if i == len(bookmarks) - 1:  # Last bookmark
                    page_num_next_bookmark = len(pdf_reader.pages)  # To end of pdf
                else:
                    page_num_next_bookmark = pdf_reader.get_destination_page_number(
                        bookmarks[i + 1]
                    )

                # Create a new PDF with just the bookmarked section
                pdf_writer = PyPDF2.PdfWriter()
                for j in range(page_num_next_bookmark - page_num_current_bookmark):
                    pdf_writer.add_page(pdf_reader.pages[page_num_current_bookmark + j])

                new_metadata = metadata.copy()

                new_metadata["/Tags"] = f"{part_names[i]}"
                pdf_writer.add_metadata(new_metadata)
                output_file_path = (
                    f"{output_directory}/{metadata['/Title']} - {part_names[i]}.pdf"
                )

                with open(output_file_path, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)

                print(f"Extracted part '{part_names[i]}' to '{output_file_path}'.")

    except FileNotFoundError:
        print(f"File not found: {score_pdf}")
    except TypeError:
        print('File supplied is not of the .pdf format.')
    except ValueError:
        print('Supplied pdf with bookmarks does not match the supplied number of part names')