const LocationService = {
  async getCurrentLocation() {
    if (!navigator.geolocation) {
      console.error("❌ Geolocation not supported by browser.");
      return null;
    }

    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => {
          console.error("⚠️ Geolocation error:", error.message);
          resolve(null);
        },
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 0,
        }
      );
    });
  }
};

export default LocationService;
