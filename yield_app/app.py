import pandas as pd
import pickle
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

# Load your dataset (update with your actual file path)
data = pd.read_csv('yield.csv')

# Check for missing values in the dataset
print("Missing values before cleaning:")
print(data.isnull().sum())

# Handle missing values:
imputer = SimpleImputer(strategy='mean')
data[['Rainfall', 'Humidity', 'Temperature', 'PH', 'Fertilizer']] = imputer.fit_transform(data[['Rainfall', 'Humidity', 'Temperature', 'PH', 'Fertilizer']])

# Drop rows with missing 'Yield' values (as it's the target)
data = data.dropna(subset=['Yield'])

# Verify that missing values are handled
print("Missing values after cleaning:")
print(data.isnull().sum())

# Define your features (X) and target (y)
X = data[['Acre', 'Crop', 'Rainfall', 'Humidity', 'Temperature', 'PH', 'Fertilizer']]
y = data['Yield']

# Encode 'Crop' as a categorical feature
encoder = LabelEncoder()
X['Crop'] = encoder.fit_transform(X['Crop'])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
model = DecisionTreeRegressor()
model.fit(X_train, y_train)

# Save the model and the encoder using pickle
with open('yield_predictor_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('label_encoders.pkl', 'wb') as f:
    pickle.dump({'Crop': encoder}, f)

print("Model and encoders saved successfully!")
from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

app = Flask(__name__)

# Load the trained model and encoders
with open('yield_predictor_model.pkl', 'rb') as f:
    yield_model = pickle.load(f)

with open('label_encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)

@app.route('/')
def home():
    return render_template('yield.html', crops=encoders['Crop'].classes_)

@app.route('/predict_yield', methods=['POST'])
def predict_yield():
    try:
        # Parse input data from the JSON request
        data = request.json
        acre = float(data.get('acre', 0))
        crop = data.get('crop')
        rainfall = float(data.get('rainfall', 0))
        humidity = float(data.get('humidity', 0))
        temperature = float(data.get('temperature', 0))
        soil_ph = float(data.get('soilPh', 0))
        fertilizer = float(data.get('fertilizer', 0))

        # Encode categorical data (crop)
        if crop not in encoders['Crop'].classes_:
            raise ValueError("Invalid crop value")
        crop_encoded = encoders['Crop'].transform([crop])[0]

        # Prepare input features for prediction
        features = [[acre, crop_encoded, rainfall, humidity, temperature, soil_ph, fertilizer]]

        # Predict yield using the model
        predicted_yield = yield_model.predict(features)[0]

        # Return prediction results
        return jsonify({
            "crop": crop,
            "acre": acre,
            "predicted_yield": round(predicted_yield, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)


