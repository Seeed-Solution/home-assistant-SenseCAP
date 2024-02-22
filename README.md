<p align="center">
  <a href="https://wiki.seeedstudio.com/home_assistant_sensecap/">
    <img src="https://raw.githubusercontent.com/Seeed-Solution/home-assistant-SenseCAP/main/icon.png" width="auto" height="auto" alt="SenseCAP">
  </a>
</p>

<div align="center">

# SenseCAP LoRaWAN Sensors Integration with Home Assistant: Streamline Your Smart Home Setup
</div>

## Installation Guide

Simplify your smart home integration with the SenseCAP LoRaWAN sensors through our straightforward installation process. Choose between an automated installation via HACS or a manual setup.

### Automated Installation via HACS

1. Navigate to **[HACS](https://hacs.xyz/) > Integrations > Plus**.
2. Search for **Seeed Studio-SenseCAP** and select **Install**.

### Manual Setup

1. Download the `sensecap` folder from the [latest release](https://github.com/Seeed-Solution/home-assistant-SenseCAP/releases/latest).
2. Copy the folder into your Home Assistant's `/config/custom_components` directory.

## Configuration Steps

Effortlessly integrate Seeed Studio-SenseCAP sensors into your Home Assistant setup with these simple steps:

1. Go to **Settings > Integrations > Add Integration**.
2. Search for **Seeed Studio-SenseCAP**. If it's not listed, *clear your browser cache and try again*.

### Completing Integration Configuration

1. Launch the integration interface to view the default MQTT topic: `application/#`. Click **Submit** to finalize the integration settings.
2. Select **notifications** at the bottom left corner. Await the new device identification alert, then click **Check it out** to proceed to device management.
3. Follow prompts to complete all integration configurations for a seamless experience.

## Tutorial Documentation

For a detailed walkthrough and advanced configurations, visit our [Wiki page](https://wiki.seeedstudio.com/home_assistant_sensecap/).

![SenseCAP M2 with Home Assistant](https://files.seeedstudio.com/wiki/IMAGES/SenseCAP/M2_homeassistant/overview.jpg)

### Integration Mechanism

The integration operates by connecting LoRa-based SenseCAP sensors to the SenseCAP M2 Multi-Platform Gateway. It utilizes the MQTT component in ChirpStack to establish a connection with the MQTT server on Home Assistant, ensuring a smooth and reliable data flow for your smart home devices.

```mermaid
graph LR
    A[SenseCAP LoRaWAN Sensors] -->|LoRa| B[SenseCAP M2 Multi-Platform Gateway]
    B -->|ChirpStack MQTT| D[Home Assistant MQTT Server]
    D -->|Integration| E[Home Assistant]

    style A fill:#eaffd0,stroke:#333,stroke-width:4px
    style B fill:#ffccf9,stroke:#333,stroke-width:4px
    style D fill:#c1f0f6,stroke:#333,stroke-width:4px
    style E fill:#eaffd0,stroke:#333,stroke-width:4px
```

