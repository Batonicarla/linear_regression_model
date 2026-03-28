Work-Life Balance Score Predictor


Mission & Problem


As a software engineer focused on older adult wellbeing, this project predicts an individual's
Work-Life Balance Score from 21 daily lifestyle indicators (sleep, stress, meditation, social
connections, physical activity) using the Kaggle Wellbeing & Lifestyle dataset (15,972 rows. 24 columns).
Three models were compared : SGD Linear Regression, Decision Tree, and Random Forest to identify which habits most influence wellbeing and power a live prediction API.


Live API — Swagger UI

Click the link below to open the Swagger UI and test the API:

 https://linear-regression-model-adn0.onrender.com/docs

Accepts POST /predict requests with 21 lifestyle input variables
Returns the predicted Work-Life Balance Score (range ≈ 480–820)
All inputs have enforced data types and range constraints


Video Demo

https://go.screenpal.com/watch/cOeuiwnTO2a


How to Run the Mobile App


Prerequisites

Flutter SDK version ≥ 3.3.0 installed
An Android emulator or a physical Android/iOS device connected and recognised by Flutter
Run flutter doctor to confirm your setup is ready

Step 1 — Clone the repository
git clone https://github.com/Batonicarla/linear_regression_model
cd linear_regression_model

Step 2 — Set your API URL
Open summative/FlutterApp/lib/main.dart and on line 12 replace the placeholder with your live Render URL:
const String kApiBase = 'https://linear-regression-model-adn0.onrender.com';

Step 3 — Install dependencies
cd summative/FlutterApp
flutter pub get

Step 4 — Run the app
flutter run

The app will launch on your connected device or emulator.

Step 5 — Make a prediction
Enter values in all 21 text fields
Tap the Predict button
The predicted Work-Life Balance Score appears in the result area below the button

Repository Structure


linear_regression_model/

└── summative/

    ├── linear_regression/
    
    │   └── multivariate_final.ipynb 
    
    ├── API/
    │   ├── prediction.py  
    
    │   ├── requirements.txt
    │   ├── best_model.pkl  
    
    │   ├── scaler.pkl  
    
    │   └── feature_columns.pkl  
    
    └── FlutterApp/
    
        ├── pubspec.yaml
        
        └── lib/
        
            └── main.dart              


Dataset
Wellbeing and Lifestyle Data — https://www.kaggle.com/datasets/ydalat/lifestyle-and-wellbeing-data 15,972 rows · 24 columns 

