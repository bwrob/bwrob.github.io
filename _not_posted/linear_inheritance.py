from typing import Any


class LinearBase:
    """A base class that enforces single inheritance.

    It provides utilities for traversing the linear inheritance chain.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        if len(cls.__bases__) > 1:
            msg = f"No multiple inheritance allowed for class {cls.__name__}"
            raise TypeError(msg)

    def get_ancestor(self, levels_up: int) -> type:
        """Retrieve a specific ancestor class by moving up the inheritance chain.

        Args:
            levels_up (int): Number of levels to traverse up.

        Returns:
            type: The ancestor class at the specified level.

        Raises:
            ValueError: If the traversal goes beyond the top of the hierarchy.

        """
        if levels_up < 0:
            msg = "levels_up must be non-negative"
            raise ValueError(msg)

        target_class = self.__class__
        for i in range(levels_up):
            if not target_class.__bases__:
                msg = (
                    f"Cannot go {levels_up} levels up; "
                    f"stopped at {target_class.__name__} (level {i})"
                )
                raise ValueError(msg)
            target_class = target_class.__bases__[0]
        return target_class


class Grandparent(LinearBase):
    def speak(self) -> None:
        print("Grandparent speaking")


class Parent(Grandparent):
    def speak(self) -> None:
        print("Parent speaking")


class Child(Parent):
    def speak(self) -> None:
        print("Child speaking...")
        # Dynamically jump 2 levels up
        self.get_ancestor(2).speak(self)


if __name__ == "__main__":
    child = Child()
    child.speak()
