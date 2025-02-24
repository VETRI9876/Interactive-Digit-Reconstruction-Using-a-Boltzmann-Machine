import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
import pickle
import os

# Define RBM class
class RBM:
    def __init__(self, num_visible, num_hidden):
        self.num_visible = num_visible
        self.num_hidden = num_hidden
        
        # Initialize weights and biases
        self.weights = tf.Variable(tf.random.normal([num_visible, num_hidden], stddev=0.01), name="weights")
        self.visible_bias = tf.Variable(tf.zeros([num_visible]), name="visible_bias")
        self.hidden_bias = tf.Variable(tf.zeros([num_hidden]), name="hidden_bias")
    
    def sample_hidden(self, visible):
        hidden_activations = tf.matmul(visible, self.weights) + self.hidden_bias
        hidden_probs = tf.nn.sigmoid(hidden_activations)
        return hidden_probs
    
    def sample_visible(self, hidden):
        visible_activations = tf.matmul(hidden, tf.transpose(self.weights)) + self.visible_bias
        visible_probs = tf.nn.sigmoid(visible_activations)
        return visible_probs
    
    def contrastive_divergence(self, visible):
        hidden_probs = self.sample_hidden(visible)
        hidden_states = hidden_probs > tf.random.uniform(hidden_probs.shape)  # Stochastic hidden states
        
        # Cast hidden states to float32 before using in matmul
        hidden_states = tf.cast(hidden_states, tf.float32)
        
        visible_reconstructed = self.sample_visible(hidden_states)
        hidden_reconstructed = self.sample_hidden(visible_reconstructed)
        
        positive_grad = tf.matmul(tf.transpose(visible), hidden_probs)
        negative_grad = tf.matmul(tf.transpose(visible_reconstructed), hidden_reconstructed)
        
        return positive_grad, negative_grad, visible_reconstructed

# Train RBM
def train_rbm(rbm, data, epochs, batch_size, learning_rate):
    optimizer = tf.keras.optimizers.Adam(learning_rate)
    
    for epoch in range(epochs):
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            with tf.GradientTape() as tape:
                positive_grad, negative_grad, visible_reconstructed = rbm.contrastive_divergence(batch)
                loss = tf.reduce_mean(tf.square(batch - visible_reconstructed))
            
            gradients = tape.gradient(loss, [rbm.weights, rbm.visible_bias, rbm.hidden_bias])
            optimizer.apply_gradients(zip(gradients, [rbm.weights, rbm.visible_bias, rbm.hidden_bias]))
        
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.numpy():.4f}")

# Main training function
def main():
    # Load and preprocess MNIST dataset
    (x_train, _), _ = mnist.load_data()
    x_train = x_train.reshape(-1, 784).astype("float32") / 255.0
    
    # RBM parameters
    num_visible = 784
    num_hidden = 128
    learning_rate = 0.01
    batch_size = 64
    epochs = 5
    
    # Initialize RBM
    rbm = RBM(num_visible, num_hidden)
    
    # Train RBM
    train_rbm(rbm, x_train, epochs, batch_size, learning_rate)
    
    # Save the trained model
    model_data = {
        "weights": rbm.weights.numpy(),
        "visible_bias": rbm.visible_bias.numpy(),
        "hidden_bias": rbm.hidden_bias.numpy(),
    }
    model_path = "D:/Interactive Digit Reconstruction Using a Boltzmann Machine/model"
    os.makedirs(model_path, exist_ok=True)
    with open(os.path.join(model_path, "rbm_model.pkl"), "wb") as f:
        pickle.dump(model_data, f)
    
    print("Model saved successfully!")

if __name__ == "__main__":
    main()
