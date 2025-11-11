# NumPy Compatibility Fix

## Issue
OpenCV (cv2) was compiled with NumPy 1.x and cannot run with NumPy 2.x.

## Solution
Downgrade NumPy to version < 2.0

## Steps to Fix

1. **Activate your virtual environment** (if using one):
   ```bash
   # Windows
   backend\backend_env\Scripts\activate
   
   # Linux/Mac
   source backend/backend_env/bin/activate
   ```

2. **Install compatible NumPy version**:
   ```bash
   pip install "numpy<2.0" --force-reinstall
   ```

3. **Reinstall all requirements** (recommended):
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

## Verification
After installation, verify NumPy version:
```python
import numpy as np
print(np.__version__)  # Should show 1.x.x, not 2.x.x
```

## Note
The requirements.txt has been updated to pin NumPy to < 2.0 to prevent this issue in the future.

