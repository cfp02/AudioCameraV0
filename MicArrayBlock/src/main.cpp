#include <Arduino.h>
#include <driver/i2s.h>

// Configuration settings
#define SAMPLE_BUFFER_SIZE 512
#define SAMPLE_RATE 8000

// Shared clock pins for both I2S peripherals
#define I2S_SCK GPIO_NUM_7     // Shared Serial clock (GPIO7)
#define I2S_WS GPIO_NUM_8      // Shared Word select (GPIO8)

// Data pins for each I2S peripheral
#define I2S_0_SD GPIO_NUM_9    // Serial data for first pair (GPIO9)
#define I2S_1_SD GPIO_NUM_6    // Serial data for second pair (GPIO6)

// I2S configuration for both peripherals
i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

// Pin configuration for first pair of microphones
i2s_pin_config_t i2s_0_pins = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_0_SD
};

// Pin configuration for second pair of microphones
i2s_pin_config_t i2s_1_pins = {
    .bck_io_num = I2S_SCK,    // Using same clock
    .ws_io_num = I2S_WS,      // Using same word select
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_1_SD
};

// Buffers for storing samples from both I2S peripherals
int32_t raw_samples_0[SAMPLE_BUFFER_SIZE * 2];  // For I2S_NUM_0
int32_t raw_samples_1[SAMPLE_BUFFER_SIZE * 2];  // For I2S_NUM_1
int16_t converted_samples[SAMPLE_BUFFER_SIZE * 4];  // Combined buffer for all 4 channels

void setup() {
    Serial.begin(115200);
    delay(1000);  // Give serial time to connect
    
    Serial.println("\n\nInitializing I2S microphones...");
    
    // Initialize first I2S peripheral
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.println("Failed to install first I2S driver!");
        while(1);
    }
    
    err = i2s_set_pin(I2S_NUM_0, &i2s_0_pins);
    if (err != ESP_OK) {
        Serial.println("Failed to set first I2S pins!");
        while(1);
    }

    // Initialize second I2S peripheral
    err = i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.println("Failed to install second I2S driver!");
        while(1);
    }
    
    err = i2s_set_pin(I2S_NUM_1, &i2s_1_pins);
    if (err != ESP_OK) {
        Serial.println("Failed to set second I2S pins!");
        while(1);
    }

    // Try to synchronize the two I2S peripherals
    i2s_stop(I2S_NUM_0);
    i2s_stop(I2S_NUM_1);
    delay(100);
    i2s_start(I2S_NUM_0);
    i2s_start(I2S_NUM_1);
    
    Serial.println("All I2S microphones initialized!");
    Serial.println("Streaming raw audio values...");
    Serial.println("Format: MIC1,MIC2,MIC3,MIC4");
    Serial.println("Run the Python script to visualize the audio.");
}

void loop() {
    size_t bytes_read_0 = 0;
    size_t bytes_read_1 = 0;
    
    // Read from both I2S peripherals
    i2s_read(I2S_NUM_0, raw_samples_0, sizeof(int32_t) * SAMPLE_BUFFER_SIZE * 2, &bytes_read_0, portMAX_DELAY);
    i2s_read(I2S_NUM_1, raw_samples_1, sizeof(int32_t) * SAMPLE_BUFFER_SIZE * 2, &bytes_read_1, portMAX_DELAY);
    
    size_t samples_read = bytes_read_0 / sizeof(int32_t);  // Should be same for both peripherals
    
    // Convert and send samples from all channels
    for (int i = 0; i < samples_read; i += 2) {
        // Convert 32-bit to 16-bit and invert for all channels
        int16_t mic1 = -(raw_samples_0[i] >> 14);      // First I2S, Left channel (reduced shift for more gain)
        int16_t mic2 = -(raw_samples_0[i + 1] >> 14);  // First I2S, Right channel
        int16_t mic3 = -(raw_samples_1[i] >> 14);      // Second I2S, Left channel
        int16_t mic4 = -(raw_samples_1[i + 1] >> 14);  // Second I2S, Right channel
        
        // Send as CSV format: "mic1,mic2,mic3,mic4"
        Serial.print(mic1);
        Serial.print(",");
        Serial.print(mic2);
        Serial.print(",");
        Serial.print(mic3);
        Serial.print(",");
        Serial.println(mic4);
    }
}