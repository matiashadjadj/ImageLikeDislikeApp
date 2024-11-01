import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sqlite3
from database import setup_database, fetch_images_from_db, update_image_status, add_image_to_db

class ActionLogger:
    """Class to handle the action logging window."""
    def __init__(self, root):
        self.root = root
        self.root.title("Action Logger")

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.label = tk.Label(self.frame, text="User Actions:")
        self.label.pack()

        self.text_area = tk.Text(self.frame, height=10, width=50)
        self.text_area.pack()

        self.total_label = tk.Label(self.frame, text="Total Likes: 0 | Total Dislikes: 0")
        self.total_label.pack()

        # Initialize like and dislike counters
        self.total_likes = 0
        self.total_dislikes = 0

        # Add a Reset Results button
        self.reset_button = tk.Button(self.frame, text="Reset Results", command=self.clear_actions)
        self.reset_button.pack()

    def log_action(self, filename, liked):
        """Log the action in the text area."""
        action = "Liked" if liked else "Disliked" if liked is not None else "No more images available."
        self.text_area.insert(tk.END, f"{filename} - {action}\n")
        self.text_area.see(tk.END)

        # Update counters
        if liked is True:
            self.total_likes += 1
        elif liked is False:
            self.total_dislikes += 1

        # Update total counts display
        self.total_label.config(text=f"Total Likes: {self.total_likes} | Total Dislikes: {self.total_dislikes}")

    def clear_actions(self):
        """Clear the logged actions and reset counters."""
        self.text_area.delete(1.0, tk.END)
        self.total_likes = 0
        self.total_dislikes = 0
        self.total_label.config(text="Total Likes: 0 | Total Dislikes: 0")

class DatingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dating App")

        # Set window size and disable resizing
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Initialize database and action logger
        setup_database()
        self.images = []  # Temporary list of images for current session
        self.current_index = 0

        # Initialize action logger window
        self.action_logger_window = tk.Toplevel(root)
        self.action_logger = ActionLogger(self.action_logger_window)

        # Create UI components
        self.image_label = tk.Label(root)
        self.image_label.pack(expand=True, fill=tk.BOTH)  # Ensures the image is centered and scales if needed


        self.counter_label = tk.Label(root, text="")
        self.counter_label.pack()

        # Place buttons at fixed coordinates
        self.import_button = tk.Button(root, text="Import Images", command=self.import_images)
        self.import_button.place(x=220, y=550) 

        self.like_button = tk.Button(root, text="Like", command=self.like)
        self.like_button.place(x=150, y=550) 

        self.dislike_button = tk.Button(root, text="Dislike", command=self.dislike)
        self.dislike_button.place(x=350, y=550)


    def show_image(self):
        """Display the current image and update the counter."""
        if self.images:
            if self.current_index < len(self.images):
                img_path = self.images[self.current_index]
                try:
                    img = Image.open(img_path)
                    
                    # Resize while maintaining aspect ratio
                    max_size = (500, 500)  # Maximum size
                    img.thumbnail(max_size)  # This maintains aspect ratio

                    img = ImageTk.PhotoImage(img)
                    self.image_label.config(image=img)
                    self.image_label.image = img
                    self.counter_label.config(text=f"Image {self.current_index + 1} of {len(self.images)}")
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.current_index += 1  # Skip to the next image
                    self.show_image()
            else:
                # Instead of quitting, show a message in the action logger
                self.action_logger.log_action("No more images available.", None)
        else:
            self.action_logger.log_action("No images available to display.", None)

    def like(self):
        """Handle the like action."""
        self.update_image_status(True)
        self.current_index += 1
        self.show_image()

    def dislike(self):
        """Handle the dislike action."""
        self.update_image_status(False)
        self.current_index += 1
        self.show_image()

    def log_user_action(self, filename, liked):
        """Log a user action (like or dislike) in the database."""
        conn = sqlite3.connect('dating_app.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_actions (filename, liked) VALUES (?, ?)', (filename, liked))
        conn.commit()
        conn.close()

    def update_image_status(self, liked):
        """Update the liked status in the database and log the user action."""
        filename = os.path.basename(self.images[self.current_index])
        update_image_status(filename, liked)  # Update the status in the images table
        self.log_user_action(filename, liked)  # Log the user action in the user_actions table
        self.action_logger.log_action(filename, liked)  # Log the action in the action logger window

    def import_images(self):
        """Open a folder dialog to select images and import them temporarily for the session."""
        try:
            # Prompt the user to select a directory
            directory = filedialog.askdirectory(title="Select a Folder with Images")
            
            if directory:
                # Clear the current session images and reset the index
                self.images = []
                self.current_index = 0

                # Load image paths into the session from the selected folder
                for file_name in os.listdir(directory):
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(directory, file_name)
                        self.images.append(file_path)  # Add the file path to the list of images

                if self.images:
                    self.show_image()  # Display the first image
                else:
                    messagebox.showinfo("Info", "No images found in the selected folder.")
            else:
                messagebox.showinfo("Info", "No folder selected.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while importing images: {e}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = DatingApp(root)
    root.mainloop()