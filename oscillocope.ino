
const float Vref = 3.3; 
const uint16_t ADCmax = 4095;

void setup() {
  // Initialize Serial for communication with STM32 and PC
  Serial.begin(9600); // Match this baud rate to the STM32's UART configuration
}

void loop() {
  if (Serial.available() >= 2) { // Check if at least 2 bytes are available
    uint16_t highByte = Serial.read(); // Read the first byte (higher part)
    uint16_t lowByte = Serial.read(); // Read the second byte (lower part)
    uint16_t adcValue = (highByte << 4) | lowByte; // Reconstruct the 12-bit ADC value
    float voltage = (adcValue / (float)ADCmax) * Vref;
    Serial.println(voltage);
  }
}