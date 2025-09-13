# EXIF Data Remover 🛡️
*`*caution:This is an AI generated README and (and so is the entire project)*`*
A local web application for removing EXIF metadata from images while preserving quality. Your privacy-focused solution for cleaning image metadata before sharing.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![Pillow](https://img.shields.io/badge/pillow-10.0-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## ✨ Features

- **Privacy First**: Remove EXIF data (GPS, camera info, timestamps) from images
- **High Quality**: Preserve image quality while stripping metadata
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **User-Friendly**: Drag & drop interface with clean, responsive design
- **Secure**: Files processed locally, automatically deleted after download
- **Extensible**: Modular architecture for future format support (PDF, etc.)

## 📋 Supported Formats

- **Images**: JPG, JPEG, PNG, TIFF, BMP
- **Future**: PDF metadata removal (planned)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
```bash
git clone <your-repo-url>
cd exif-remover
```

2. **Install dependencies**
```bash
python -m pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open your browser**
```
http://localhost:4001
```

## 🎯 Usage

1. **Upload**: Drag & drop an image or click to browse
2. **Process**: Watch the progress as EXIF data is removed
3. **Review**: See what metadata was found and removed
4. **Download**: Get your clean image with one click

## 🏗️ Architecture

```
exif-remover/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main frontend template
├── static/
│   ├── style.css      # Responsive styling
│   └── script.js      # Frontend functionality
├── uploads/           # Temporary upload storage
└── processed/         # Temporary processed files
```

### Key Components

- **Backend**: Flask server with Pillow for image processing
- **Frontend**: Vanilla HTML/CSS/JavaScript with responsive design
- **Processing**: Modular `FileProcessor` class for easy format extension
- **Security**: Automatic file cleanup and size limits

## 🔧 Configuration

### Environment Variables

The application can be configured using environment variables:

```bash
# Port number (default: 4001)
export PORT=8080

# Host address (default: 0.0.0.0)
export HOST=127.0.0.1

# Max file size (default: 50MB)
export MAX_FILE_SIZE=100000000
```

### File Size Limits

Default maximum file size: **50MB**  
To change: Modify `app.config['MAX_CONTENT_LENGTH']` in `app.py`

## 🛠️ Development

### Adding New Formats

The architecture is designed for easy extension. To add PDF support:

1. Install additional dependencies:
```bash
python -m pip install PyPDF2
```

2. Add processing method to `FileProcessor`:
```python
@staticmethod
def process_pdf(input_path, output_path):
    # PDF metadata removal logic
    pass
```

3. Update file type validation in both frontend and backend

### Running in Development Mode

```bash
python app.py
```

The app will run with debug mode enabled and auto-reload on changes.

### Production Deployment

For production use, consider using a WSGI server:

```bash
python -m pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:4001 app:app
```

## 📊 Technical Details

### EXIF Data Removed

- GPS coordinates
- Camera make/model
- Date/time stamps
- Exposure settings
- Thumbnail data
- And all other EXIF metadata

### Processing Pipeline

1. File upload validation
2. Temporary storage
3. EXIF extraction (for display)
4. Metadata removal
5. Quality-preserving compression
6. Secure download
7. Automatic cleanup

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed description
2. **Suggest Features**: Share your ideas for improvement
3. **Submit PRs**: Follow the existing code style and architecture

### Planned Features

- [ ] PDF metadata removal
- [ ] Batch processing
- [ ] CLI interface
- [ ] Docker container
- [ ] Progressive Web App (PWA) support

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'PIL'**
```bash
python -m pip install Pillow
```

**"413 Request Entity Too Large"**
- The file exceeds the 50MB limit
- Modify `MAX_CONTENT_LENGTH` in `app.py` if needed

**Port already in use**
```bash
# Use a different port
# app.run(debug=True, host='0.0.0.0', port=4001) change port number from 4001 to something else
python app.py
```

### Getting Help

1. Check the [Issues](../../issues) for existing solutions
2. Create a new issue with:
   - Python version (`python --version`)
   - Error messages
   - Steps to reproduce

## 🙏 Acknowledgments

- **Pillow Library**: For excellent image processing capabilities
- **Flask Framework**: For simple and powerful web application foundation
- **Open Source Community**: For inspiration and best practices

---

**Privacy Matters** 🔒 Your images are processed locally and never leave your computer. No cloud storage, no data collection, just pure privacy protection.

*Made with ❤️ for the privacy-conscious community*
