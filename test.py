import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
import os

# Paths to dataset directories (Ensure these paths are correct)
base_dir = 'dataset'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')

# Image data generators with basic preprocessing (no augmentation)
train_datagen = ImageDataGenerator(rescale=1./255)
validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(64, 64),  # Smaller image size for faster training
    batch_size=16,  # Smaller batch size for faster training
    class_mode='binary'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(64, 64),
    batch_size=16,
    class_mode='binary'
)

# Simple CNN model
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Train the model for just a couple of epochs to keep it fast
history = model.fit(
    train_generator,
    steps_per_epoch=5,  # Only a few steps per epoch
    epochs=3,  # Very few epochs to keep it fast
    validation_data=validation_generator,
    validation_steps=2
)

# Save the trained model
model.save('simple_model.keras')

print("Model training complete and saved as 'simple_model.keras'")
loaded_model = load_model('simple_model.keras')
loaded_model.summary()