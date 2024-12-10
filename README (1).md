
# BizCard OCR Application

BizCard OCR is a Streamlit-based application designed to extract, organize, and manage business card data using Optical Character Recognition (OCR). This application uses EasyOCR for text extraction and SQLite for storing and managing extracted details.

## Features

1. **OCR-based Text Extraction**: Extracts text from uploaded business card images.
2. **Categorized Data**: Organizes extracted text into categories like Name, Designation, Contact, Email, and more.
3. **Data Management**:
   - Save extracted data to an SQLite database.
   - Preview and modify saved records.
   - Delete specific records from the database.
4. **User-friendly Interface**: Built with Streamlit for seamless interaction.

## Prerequisites

Ensure the following dependencies are installed:

- Python 3.7+
- Streamlit
- EasyOCR
- PIL (Pillow)
- pandas
- numpy
- sqlite3

Install dependencies using:
```bash
pip install streamlit easyocr pillow pandas numpy
```

## How to Use

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

3. **Navigate Through the Application**:
   - **Home**: Introductory page.
   - **Upload & Modifying**:
     - Upload business card images.
     - Extract text and preview organized details.
     - Save data to the database.
     - Modify saved records.
   - **Delete**:
     - Select and delete specific records by Name and Designation.

## Application Logic

1. **Text Extraction**:
   - The application uses EasyOCR to extract text from images.
   - Extracted text is structured into predefined categories.

2. **Database Management**:
   - SQLite is used to store and manage data.
   - Users can view, modify, or delete records as needed.

## 🔑 Key Functions

### `image_to_text(path)`
- Converts uploaded image into text using EasyOCR.

### `Extracted_text(texts)`
- Structures extracted text into predefined categories:
  - Name
  - Designation
  - Company Name
  - Contact
  - Email
  - Website
  - Address
  - Pincode

---

## 📂 Database Structure

Table Name: `bizcard_details`

| Column       | Data Type   |
|--------------|-------------|
| name         | TEXT        |
| designation  | TEXT        |
| company_name | TEXT        |
| contact      | TEXT        |
| email        | TEXT        |
| website      | TEXT        |
| address      | TEXT        |
| pincode      | TEXT        |
| image        | BLOB        |

---

## File Structure

- `app.py`: Main application file.
- `Bizcard_data.db`: SQLite database file (generated automatically upon first save).
- `README.md`: Documentation file.

## Future Enhancements

- Support for multi-language OCR.
- Advanced text matching for better categorization.
- Integration with cloud-based databases.

## License

This project is licensed under the MIT License.
