from zipfile import ZipFile as zipf
import os

def format_receipt(book_dict, orderID, orderQuantity, orderTime, orderPrice):
    receipt_lines = []
    
    for book_id, book_info in book_dict.items():
        receipt_lines.append(f'Book ID: {book_id}')
        receipt_lines.append(f'Title: {book_info["title"]}')
        receipt_lines.append(f'Author: {book_info["author"]}')
        receipt_lines.append(f'Publisher: {book_info["publisher"]}')
        receipt_lines.append(f'Publication Date: {book_info["publication_date"]}')
        receipt_lines.append(f'File Format: {book_info["file_format"]}')
        receipt_lines.append('Genre: ')
        for items in book_info["genre"]:
            receipt_lines.append(f'{items}')
        receipt_lines.append('--------------------------------')
        receipt_lines.append(f'Price: ${book_info["price"]:.2f}')
        receipt_lines.append(f'Discount: ${book_info["discount"]:.2f}')
        receipt_lines.append('-' * 40)  # Add a separator for each book

    # Join all the lines into a single string with newlines
    receipt_string = '\n'.join(receipt_lines)
    receipt_string = f"Thank you for purchasing with Seneca! For record keeping, your order is as follows:\nOrder ID: {orderID}\tOrder Time: {orderTime}\nOrder Quantity: {orderQuantity}\tOrder Price: {orderPrice}\n" + receipt_string
    print(receipt_string)
    
    return receipt_string

def createZip(filename, contents):
    pathPrefix = os.environ.get('books')
    zipPathPrefix = os.environ.get('zip dumps')

    if not pathPrefix:
        raise ValueError("CRITICAL: ENVIRONMENT VARIABLE FOR BOOKS IS NOT SET")
    if not zipPathPrefix:
        raise ValueError("CRITICAL: ENVIRONMENT VARIABLE FOR ZIP FOLDER IS NOT SET")
    
    print(pathPrefix, zipPathPrefix)
    zip_path = os.path.join(zipPathPrefix, filename) + ".zip"
    print(zip_path)

    with zipf(zip_path, "w") as zipPackage:
        for file in contents:
            full_path = os.path.join(pathPrefix, file[1:])
            arcname = os.path.basename(full_path)
            zipPackage.write(filename=full_path, arcname=arcname)
    return zip_path