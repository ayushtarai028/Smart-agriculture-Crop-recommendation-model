import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

# Load the dataset
url = "https://raw.githubusercontent.com/AbhishekSenguptaGit/Crop-Recommendation/refs/heads/master/cropdata.csv"
data = pd.read_csv(url)

# Clean column names by removing leading/trailing whitespaces
data.columns = data.columns.str.strip()

# Handle missing values
data = data.dropna()

# Encoding categorical variables (Crop and Soil_Type)
label_encoder_crop = LabelEncoder()
data['Crops to be taken'] = label_encoder_crop.fit_transform(data['Crops to be taken'])

label_encoder_soil = LabelEncoder()
data['Soil Type'] = label_encoder_soil.fit_transform(data['Soil Type'])  # Encoding soil type

# Splitting the data into features (X) and target (y)
X = data.drop(columns=['Crops to be taken'])
y = data['Crops to be taken']

# Split the data into training (80%), validation (10%), and testing (10%) sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)
X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Scaling/Normalizing numerical features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_valid_scaled = scaler.transform(X_valid)
X_test_scaled = scaler.transform(X_test)

# Train models
mlp = MLPClassifier(hidden_layer_sizes=(50,), max_iter=1000, random_state=42)
gnb = GaussianNB()
knn = KNeighborsClassifier(n_neighbors=5)
log_reg = LogisticRegression(max_iter=1000)

mlp.fit(X_train_scaled, y_train)
gnb.fit(X_train_scaled, y_train)
knn.fit(X_train_scaled, y_train)
log_reg.fit(X_train_scaled, y_train)

# Combine models using a Voting Classifier
voting_clf = VotingClassifier(estimators=[
    ('mlp', mlp),
    ('gnb', gnb),
    ('knn', knn),
    ('log_reg', log_reg)
], voting='hard')

# Train the Voting Classifier
voting_clf.fit(X_train_scaled, y_train)

# Save the trained model, scaler, and label encoders
joblib.dump(voting_clf, 'crop_recommendation_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoder_crop, 'label_encoder_crop.pkl')
joblib.dump(label_encoder_soil, 'label_encoder_soil.pkl')

# Flask API Implementation
app = Flask(__name__)
CORS(app)

# Load models and scalers
voting_clf = joblib.load('crop_recommendation_model.pkl')
scaler = joblib.load('scaler.pkl')
label_encoder_crop = joblib.load('label_encoder_crop.pkl')
label_encoder_soil = joblib.load('label_encoder_soil.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Check for required keys
        required_keys = ['Soil Type', 'Soil depth(cm)', 'pH', 'Bulk density Gm/cc', 'Ec (dsm-1)', 'Organic carbon (%)', 
                         'Soil moisture retention  (%)', 'Available water capacity(m/m)', 
                         'Infiltration rate cm/hr', 'Clay %']
        
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Missing key: {key}'}), 400

        # Extract features from the JSON input
        soil_type = data['Soil Type']
        soil_depth = data['Soil depth(cm)']
        ph = data['pH']
        bulk_density = data['Bulk density Gm/cc']
        ec = data['Ec (dsm-1)']
        organic_carbon = data['Organic carbon (%)']
        moisture_retention = data['Soil moisture retention  (%)']
        available_water_capacity = data['Available water capacity(m/m)']
        infiltration_rate = data['Infiltration rate cm/hr']
        clay_percent = data['Clay %']

        # Map soil type to numeric value using the label encoder
        try:
            soil_type_encoded = label_encoder_soil.transform([soil_type])[0]
        except ValueError as e:
            return jsonify({'error': f'Unseen Soil Type: {soil_type}. Please provide a valid Soil Type.'}), 400

        # Create feature array
        features = np.array([[soil_type_encoded, soil_depth, ph, bulk_density, ec, organic_carbon,
                              moisture_retention, available_water_capacity, infiltration_rate, clay_percent]])

        # Scale the features
        features_scaled = scaler.transform(features)

        # Make prediction
        prediction = voting_clf.predict(features_scaled)
        
        # Decode the prediction to the crop name
        predicted_crop = label_encoder_crop.inverse_transform([prediction[0]])[0]
        
        return jsonify({'prediction': predicted_crop})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
