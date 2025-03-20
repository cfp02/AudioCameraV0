#include <Arduino.h>
#include <driver/i2s.h>

// Configuration settings
#define SAMPLE_BUFFER_SIZE 512
#define SAMPLE_RATE 8000

// Pin definitions for I2S_NUM_0
#define I2S_0_SCK GPIO_NUM_7   // Serial clock (GPIO7)
#define I2S_0_WS GPIO_NUM_8    // Word select (GPIO8)
#define I2S_0_SD1 GPIO_NUM_9   // Serial data for first mic (GPIO9)
#define I2S_0_SD2 GPIO_NUM_6   // Serial data for second mic (GPIO6)

// I2S configuration
i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,  // Changed to receive both channels
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

// Pin configuration for both microphones
i2s_pin_config_t i2s_0_pins = {
    .bck_io_num = I2S_0_SCK,
    .ws_io_num = I2S_0_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_0_SD1  // Primary mic on SD1
};

// Buffer for storing samples
int32_t raw_samples[SAMPLE_BUFFER_SIZE * 2];  // Doubled for stereo
int16_t converted_samples[SAMPLE_BUFFER_SIZE * 2];  // Doubled for stereo

void setup() {
    Serial.begin(115200);
    delay(1000);  // Give serial time to connect
    
    Serial.println("\n\nInitializing I2S microphones...");
    
    // Initialize I2S
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.println("Failed to install I2S driver!");
        while(1);
    }
    
    err = i2s_set_pin(I2S_NUM_0, &i2s_0_pins);
    if (err != ESP_OK) {
        Serial.println("Failed to set I2S pins!");
        while(1);
    }
    
    Serial.println("I2S microphones initialized!");
    Serial.println("Streaming raw audio values...");
    Serial.println("Format: LEFT_SAMPLE,RIGHT_SAMPLE");
    Serial.println("Run the Python script to visualize the audio.");
}

void loop() {
    size_t bytes_read = 0;
    
    // Read from I2S (will get both channels interleaved)
    i2s_read(I2S_NUM_0, raw_samples, sizeof(int32_t) * SAMPLE_BUFFER_SIZE * 2, &bytes_read, portMAX_DELAY);
    size_t samples_read = bytes_read / sizeof(int32_t);
    
    // Convert and send samples from both channels
    for (int i = 0; i < samples_read; i += 2) {  // Increment by 2 to handle stereo samples
        // Convert 32-bit to 16-bit and invert for both channels
        int16_t left_sample = -(raw_samples[i] >> 16);
        int16_t right_sample = -(raw_samples[i + 1] >> 16);
        
        // Send as CSV format: "left_sample,right_sample"
        Serial.print(left_sample);
        Serial.print(",");
        Serial.println(right_sample);
    }
}