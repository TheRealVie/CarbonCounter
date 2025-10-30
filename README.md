# CarbonCounter

## Setup and Installation (Windows PowerShell)

1. Navigate to the project root:

2. Create a virtual environment (only needed once):
   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Upgrade packaging tools (recommended):
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

5. Install dependencies required by the app:
   ```powershell
   pip install streamlit pandas plotly
   ```

## Run the App

From the project root with the venv activated:
```powershell
streamlit run CarbonCounter\carbon_counter.py
```

This will start Streamlit and open the Carbon Counter UI in your browser.

## Setup and Installation (macOS/Linux)

1. Navigate to the project root:

2. Create a virtual environment (only needed once):
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Upgrade packaging tools (recommended):
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

5. Install dependencies required by the app:
   ```bash
   pip install streamlit pandas plotly
   ```

### Run the App (macOS/Linux)

From the project root with the venv activated:
```bash
streamlit run CarbonCounter/carbon_counter.py
```

## Additional Notes

- To deactivate the virtual environment:
  ```powershell
  deactivate
  ```
- To save your current dependencies:
  ```powershell
  pip freeze > requirements.txt
  ```
## Final Note
   Our calculations will not be exact as there are many factors contributing to carbon emissions, however our calculations are based off reasonable estimates from the US Department of Environmental Protection.
