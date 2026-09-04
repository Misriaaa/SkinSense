import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import numpy as np
import os
import random

# === STEP 1: SETUP & SEED ===
tf.random.set_seed(42)
np.random.seed(42)
random.seed(42)

# === STEP 2: PATH SETUP ===
base_dir = "dataset/prepared"
train_dir = os.path.join(base_dir, "train")
test_dir = os.path.join(base_dir, "test")

img_size = (128, 128)
batch_size = 32
epochs = 80  # more training for better accuracy

# === STEP 3: DATA AUGMENTATION ===
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=35,
    zoom_range=0.3,
    shear_range=0.25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    brightness_range=[0.7, 1.3],
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.1
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training"
)

val_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation"
)

# === STEP 4: PRINT CLASS INFO ===
print("\n🧾 CLASS DISTRIBUTION:")
for class_name, class_idx in train_generator.class_indices.items():
    count = list(train_generator.classes).count(class_idx)
    print(f"  {class_name:<8} → {count} images")

print(f"\n📊 Total training images: {train_generator.samples}")
print(f"📊 Total validation images: {val_generator.samples}")

# === STEP 5: HANDLE CLASS IMBALANCE ===
counts = np.bincount(train_generator.classes)
max_count = np.max(counts)
class_weight = {i: max_count / count for i, count in enumerate(counts)}
print("\n⚖️ Class Weights:", class_weight)

# === STEP 6: BUILD IMPROVED CNN MODEL ===
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(128, 128, 3)),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation="relu"),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation="relu"),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(256, (3, 3), activation="relu"),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(512, activation="relu"),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# === STEP 7: CALLBACKS ===
callbacks = [
    EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True),
    ModelCheckpoint("best_skin_disease_model.h5", monitor="val_accuracy", save_best_only=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6, verbose=1)
]

# === STEP 8: TRAIN MODEL ===
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=epochs,
    class_weight=class_weight,
    callbacks=callbacks
)

# === STEP 9: TEST EVALUATION ===
test_datagen = ImageDataGenerator(rescale=1./255)
try:
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical"
    )

    loss, acc = model.evaluate(test_generator)
    print(f"\n✅ Test Accuracy: {acc:.2f}")

except Exception as e:
    print("⚠️ Some images in test data may be corrupted or unreadable.")
    print("Skipping evaluation. Error:", e)

# === STEP 10: SAVE FINAL MODEL ===
save_path = os.path.join(os.getcwd(), "skin_disease_model.h5")
model.save(save_path)
print(f"\n🎉 Final model saved successfully at: {save_path}")
