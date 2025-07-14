# PLO Comparison Platform

A comprehensive web platform that allows institutions to compare their Program Learning Outcomes (PLOs) with the Canadian Program Framework (CPF) using AI-powered semantic similarity analysis.

## Features

- **AI-Powered Analysis**: Uses state-of-the-art sentence transformers for accurate PLO comparison
- **Interactive Dashboard**: Visualize alignment scores across Knowledge, Skills, and Values themes
- **Multiple Input Methods**: Upload CSV files or enter PLOs directly
- **Detailed Reports**: Get comprehensive analysis with actionable recommendations
- **User Management**: Secure institution registration and submission tracking
- **Export Capabilities**: Download results in JSON or CSV format

## Framework Coverage

The platform compares institutional PLOs against the Canadian Program Framework, which includes:

### Knowledge Theme
- Core biological concepts (evolution, structure-function, information flow, energy transformation, systems)
- Interdisciplinary knowledge and systems thinking
- Nature of science and scientific methodology
- Biological diversity and evolutionary origins
- Structure-function relationships

### Skills Theme
- Experimental design and scientific method
- Data collection, analysis, and interpretation
- Communication (oral, written, visual)
- Collaboration and teamwork
- Laboratory, field, and technical skills
- Digital tools and computational methods
- Critical evaluation of literature
- Statistical and mathematical reasoning

### Values Theme
- Ethical responsibility in research and practice
- Societal, cultural, environmental, and global impact awareness
- Career exploration and lifelong learning
- Equity, diversity, and inclusion awareness
- Sustainability and environmental stewardship

## Installation

1. **Clone or download the platform files**
   ```bash
   cd plo-platform
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the platform**
   Open your browser and go to `http://localhost:5000`

## Usage

### For Institutions

1. **Register**: Create an account for your institution
2. **Login**: Access your dashboard
3. **Submit PLOs**: Either:
   - Enter PLOs directly in the text area (one per line)
   - Upload a CSV file with a "PLO" column
4. **Review Results**: Get detailed analysis including:
   - Overall alignment score
   - Theme-specific scores (Knowledge, Skills, Values)
   - Best matches for each PLO
   - Actionable recommendations
5. **Export**: Download results for further analysis

### Sample PLO Input

```
Apply mathematical and computational tools to analyze biological datasets.
Demonstrate ethical reasoning in professional biological contexts.
Communicate scientific concepts to both expert and non-expert audiences.
Design and conduct experiments to test biological hypotheses.
Work effectively in diverse teams to solve complex biological problems.
```

### Sample Results

The platform provides:
- **Alignment Scores**: 0-1 scale showing similarity to CPF framework
- **Theme Breakdown**: Scores for Knowledge, Skills, and Values
- **Best Matches**: Top CPF PLO matches for each institutional PLO
- **Recommendations**: Specific suggestions for improvement

## Technical Details

### Architecture
- **Backend**: Flask web framework with SQLAlchemy ORM
- **AI Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Database**: SQLite (can be configured for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5 with Chart.js for visualizations

### AI Analysis
The platform uses semantic similarity analysis to compare PLOs:
1. **Encoding**: Both institutional and CPF PLOs are converted to vector embeddings
2. **Comparison**: Cosine similarity is calculated between all pairs
3. **Scoring**: Scores are aggregated by theme and overall
4. **Recommendations**: AI-generated suggestions based on alignment gaps

### Data Security
- Passwords are hashed using Werkzeug security functions
- User data is isolated by institution
- Uploaded files are processed and deleted immediately
- No PLO data is shared between institutions

## Customization

### Adding New Frameworks
The platform can be extended to include other frameworks:
1. Add framework PLOs to `cpf_comparison.py`
2. Implement comparison logic in `CPFComparator` class
3. Update templates to display new framework results

### Modifying CPF Framework
Edit the `cpf_plos` dictionary in `cpf_comparison.py` to:
- Add new PLOs to existing themes
- Create new themes
- Modify existing PLO descriptions

### Styling and Branding
- Modify `templates/base.html` for custom styling
- Update color schemes in CSS variables
- Add institution logos and branding

## API Access

The platform provides a REST API for programmatic access:

```python
import requests

# Compare PLOs via API
response = requests.post('http://localhost:5000/api/compare', 
                        json={'plos': ['Your PLO here']})
results = response.json()
```

## Troubleshooting

### Common Issues

1. **Model Download Issues**: The sentence transformer model downloads automatically on first use. Ensure internet connectivity.

2. **Memory Issues**: For large PLO datasets, consider:
   - Processing in batches
   - Using a more powerful server
   - Implementing caching

3. **Database Issues**: If the database becomes corrupted:
   ```bash
   rm plo_platform.db
   python app.py  # This will recreate the database
   ```

### Performance Optimization

- Use a production WSGI server (Gunicorn, uWSGI)
- Configure database connection pooling
- Implement result caching for repeated comparisons
- Use a CDN for static assets

## Contributing

To contribute to the platform:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This platform is developed for educational institutions to align their learning outcomes with the Canadian Program Framework.

## Support

For technical support or questions about the Canadian Program Framework, please contact the development team.

---

**Note**: This platform is designed to support institutions in aligning their PLOs with Canadian standards. The AI analysis provides guidance but should be reviewed by educational professionals for final decisions. # Updated deployment
