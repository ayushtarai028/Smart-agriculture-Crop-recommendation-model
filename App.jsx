import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [result, setResult] = useState('');
  const [soilType, setSoilType] = useState('');
  const [soilDepth, setSoilDepth] = useState('');
  const [phLevel, setPhLevel] = useState('');
  const [bulkDensity, setBulkDensity] = useState('');
  const [ec, setEc] = useState('');
  const [organicCarbon, setOrganicCarbon] = useState('');
  const [soilMoisture, setSoilMoisture] = useState('');
  const [waterCapacity, setWaterCapacity] = useState('');
  const [infiltrationRate, setInfiltrationRate] = useState('');
  const [clayPercentage, setClayPercentage] = useState('');
  const [soilTypes, setSoilTypes] = useState([]);

  // Fetch soil types from the dataset or pre-define them
  useEffect(() => {
    const fetchSoilTypes = async () => {
      try {
        const response = await fetch('https://raw.githubusercontent.com/AbhishekSenguptaGit/Crop-Recommendation/refs/heads/master/cropdata.csv');
        const data = await response.text();
        const lines = data.split('\n');
        const header = lines[0].split(',');
        const soilTypeIndex = header.indexOf('Soil Type');
        const soilTypesSet = new Set();

        lines.slice(1).forEach(line => {
          const columns = line.split(',');
          if (columns[soilTypeIndex]) {
            soilTypesSet.add(columns[soilTypeIndex].trim());
          }
        });

        setSoilTypes([...soilTypesSet]);
      } catch (error) {
        console.error('Error fetching soil types:', error);
      }
    };

    fetchSoilTypes();
  }, []);

  const makePrediction = async () => {
    // Check if all fields are filled out
    if (!soilType || !soilDepth || !phLevel || !bulkDensity || 
        !ec || !organicCarbon || !soilMoisture || 
        !waterCapacity || !infiltrationRate || !clayPercentage) {
      setResult('Please fill out all fields before making a prediction.');
      return;
    }

    const data = {
      'Soil Type': soilType,  // Ensure soil type is passed as a string
      'Soil depth(cm)': parseFloat(soilDepth),
      'pH': parseFloat(phLevel),
      'Bulk density Gm/cc': parseFloat(bulkDensity),
      'Ec (dsm-1)': parseFloat(ec),
      'Organic carbon (%)': parseFloat(organicCarbon),
      'Soil moisture retention  (%)': parseFloat(soilMoisture),
      'Available water capacity(m/m)': parseFloat(waterCapacity),
      'Infiltration rate cm/hr': parseFloat(infiltrationRate),
      'Clay %': parseFloat(clayPercentage),
    };

    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
      }

      const resultData = await response.json();
      setResult(`Recommended Crop: ${resultData.prediction}`);
    } catch (error) {
      console.error('Error:', error);
      setResult('Error making prediction: ' + error.message);
    }
  };

  return (
    <div className="App">
      <h1>Crop Recommendation System</h1>
      <div>
        <label>Soil Type:</label>
        <select value={soilType} onChange={(e) => setSoilType(e.target.value)}>
          <option value="">Select Soil Type</option>
          {soilTypes.map((type, index) => (
            <option key={index} value={type}>{type}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Soil Depth (cm):</label>
        <input type="number" value={soilDepth} onChange={(e) => setSoilDepth(e.target.value)} />
      </div>
      <div>
        <label>pH Level:</label>
        <input type="number" value={phLevel} onChange={(e) => setPhLevel(e.target.value)} />
      </div>
      <div>
        <label>Bulk Density (Gm/cc):</label>
        <input type="number" value={bulkDensity} onChange={(e) => setBulkDensity(e.target.value)} />
      </div>
      <div>
        <label>Electrical Conductivity (dsm-1):</label>
        <input type="number" value={ec} onChange={(e) => setEc(e.target.value)} />
      </div>
      <div>
        <label>Organic Carbon (%):</label>
        <input type="number" value={organicCarbon} onChange={(e) => setOrganicCarbon(e.target.value)} />
      </div>
      <div>
        <label>Soil Moisture Retention (%):</label>
        <input type="number" value={soilMoisture} onChange={(e) => setSoilMoisture(e.target.value)} />
      </div>
      <div>
        <label>Water Capacity (m/m):</label>
        <input type="number" value={waterCapacity} onChange={(e) => setWaterCapacity(e.target.value)} />
      </div>
      <div>
        <label>Infiltration Rate (cm/hr):</label>
        <input type="number" value={infiltrationRate} onChange={(e) => setInfiltrationRate(e.target.value)} />
      </div>
      <div>
        <label>Clay Percentage:</label>
        <input type="number" value={clayPercentage} onChange={(e) => setClayPercentage(e.target.value)} />
      </div>
      <button onClick={makePrediction}>Get Crop Recommendation</button>
      <p>{result}</p>
    </div>
  );
}

export default App;
