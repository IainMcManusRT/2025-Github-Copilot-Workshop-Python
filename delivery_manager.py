from __future__ import annotations
import time
import random
import logging
import threading
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from collections import Counter


class EventArgs:
    """Base class for event arguments"""
    pass


class Event:
    """Class equivalent to C#'s event"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """Add event handler"""
        if handler not in self._handlers:
            self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """Remove event handler"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def invoke(self, sender, args: EventArgs = None):
        """Fire event"""
        for handler in self._handlers:
            try:
                handler(sender, args or EventArgs())
            except Exception as e:
                logging.error(f"Event handler error: {e}")


@dataclass
class KitchenObjectSO:
    """Kitchen object data class"""
    name: str
    object_id: int


@dataclass
class RecipeSO:
    """Recipe data class"""
    name: str
    kitchen_object_so_list: List[KitchenObjectSO] = field(default_factory=list)


@dataclass
class RecipeListSO:
    """Recipe list data class"""
    recipe_so_list: List[RecipeSO] = field(default_factory=list)


class PlateKitchenObject:
    """Plate kitchen object"""
    
    def __init__(self):
        self._kitchen_object_so_list: List[KitchenObjectSO] = []
    
    def add_kitchen_object(self, kitchen_object: KitchenObjectSO):
        """Add kitchen object"""
        self._kitchen_object_so_list.append(kitchen_object)
    
    def get_kitchen_object_so_list(self) -> List[KitchenObjectSO]:
        """Get kitchen object list"""
        return self._kitchen_object_so_list.copy()


class KitchenGameManager:
    """Kitchen game manager (Singleton)"""
    
    _instance: Optional['KitchenGameManager'] = None
    
    def __init__(self):
        self._is_game_playing = False
    
    @classmethod
    def get_instance(cls) -> 'KitchenGameManager':
        """Get Singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_game_playing(self) -> bool:
        """Check if game is in progress"""
        return self._is_game_playing
    
    def start_game(self):
        """Start game"""
        self._is_game_playing = True
    
    def stop_game(self):
        """Stop game"""
        self._is_game_playing = False


    """
    Delivery management class (Python version).
    Handles recipe spawning, delivery, and event management.
    Thread-safe singleton, testable, and extensible.
    """

    _instance = None
    _lock = threading.Lock()
    SPAWN_RECIPE_TIMER_MAX = 4.0
    WAITING_RECIPES_MAX = 4

    def __init__(self, recipe_list_so: RecipeListSO, timer: Optional[callable] = None, random_gen: Optional[callable] = None):
        # Event definitions
        self.on_recipe_spawned = Event()
        self.on_recipe_completed = Event()
        self.on_recipe_success = Event()
        self.on_recipe_failed = Event()

        # Private variables
        self._recipe_list_so = recipe_list_so
        self._waiting_recipe_so_list: List[RecipeSO] = []
        self._spawn_recipe_timer = self.SPAWN_RECIPE_TIMER_MAX
        self._successful_recipes_amount = 0
        self._last_update_time = None
        self._timer = timer if timer else time.time
        self._random = random_gen if random_gen else random.choice
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None, timer: Optional[callable] = None, random_gen: Optional[callable] = None):
        """Thread-safe singleton getter."""
        with cls._lock:
            if cls._instance is None:
                if recipe_list_so is None:
                    raise ValueError("recipe_list_so is required for initial creation")
                cls._instance = cls(recipe_list_so, timer, random_gen)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    def update(self):
        """
        Update the delivery manager, spawning recipes if needed.
        Should be called periodically (e.g., in a game loop).
        """
        now = self._timer()
        if self._last_update_time is None:
            self._last_update_time = now
        delta = now - self._last_update_time
        self._last_update_time = now

        self._spawn_recipe_timer -= delta

        if self._spawn_recipe_timer <= 0.0:
            self._spawn_recipe_timer = self.SPAWN_RECIPE_TIMER_MAX
            kitchen_game_manager = KitchenGameManager.get_instance()
            if (kitchen_game_manager.is_game_playing() and 
                len(self._waiting_recipe_so_list) < self.WAITING_RECIPES_MAX):
                # Randomly select recipe
                waiting_recipe_so = self._random(self._recipe_list_so.recipe_so_list)
                self._waiting_recipe_so_list.append(waiting_recipe_so)
                # Fire event
                self.on_recipe_spawned.invoke(self)
    
    def _ingredients_match(self, plate_ingredients: List[KitchenObjectSO], recipe_ingredients: List[KitchenObjectSO]) -> bool:
        """
        Compare two ingredient lists by object_id, ignoring order and duplicates.
        """
        plate_counter = Counter(obj.object_id for obj in plate_ingredients)
        recipe_counter = Counter(obj.object_id for obj in recipe_ingredients)
        return plate_counter == recipe_counter

    def deliver_recipe(self, plate_kitchen_object: PlateKitchenObject):
        """
        Check if the plate's ingredients match any waiting recipe.
        Fires success or failure events accordingly.
        Logs errors and important state changes.
        """
        if plate_kitchen_object is None:
            logging.warning("Attempted to deliver a None plate.")
            self.on_recipe_failed.invoke(self)
            return

        plate_ingredients = plate_kitchen_object.get_kitchen_object_so_list()
        if not plate_ingredients:
            logging.warning("Attempted to deliver an empty plate.")
            self.on_recipe_failed.invoke(self)
            return

        if not self._waiting_recipe_so_list:
            logging.warning("No waiting recipes to deliver.")
            self.on_recipe_failed.invoke(self)
            return

        for i, waiting_recipe in enumerate(self._waiting_recipe_so_list):
            if self._ingredients_match(plate_ingredients, waiting_recipe.kitchen_object_so_list):
                self._successful_recipes_amount += 1
                self._waiting_recipe_so_list.pop(i)
                logging.info(f"Recipe delivered successfully: {waiting_recipe.name}")
                self.on_recipe_completed.invoke(self)
                self.on_recipe_success.invoke(self)
                return

        logging.info("No matching recipe found for delivery.")
        self.on_recipe_failed.invoke(self)
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """Return a copy of the waiting recipe list."""
        return list(self._waiting_recipe_so_list)
    
    def get_successful_recipes_amount(self) -> int:
        """Return the number of successful recipe deliveries."""
        return self._successful_recipes_amount


# Usage example
if __name__ == "__main__":
    # Create sample data
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # Sample recipes
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # Initialize game manager and delivery manager
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # Set up event handlers
    def on_recipe_spawned(sender, args):
        print("New recipe has been generated!")
    
    def on_recipe_success(sender, args):
        print("Recipe delivery successful!")
    
    def on_recipe_failed(sender, args):
        print("Recipe delivery failed...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # Sample execution
    print("Game starting...")
    
    # Run update process for 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # Update every 100ms
    
    print(f"Number of waiting recipes: {len(delivery_manager.get_waiting_recipe_so_list())}")
    
    # Sample delivery test
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    
    print("Delivering sandwich...")
    delivery_manager.deliver_recipe(plate)
    
    print(f"Number of successful recipes: {delivery_manager.get_successful_recipes_amount()}")