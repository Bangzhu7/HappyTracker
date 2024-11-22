import flet as ft
from datetime import datetime
import calendar


class HabitTracker:
    def __init__(self):
        self.habits = []
        self.editing_habit_index = None  # Track the index of the habit being edited
        self.current_page = "habits"  # Default view is "Habit List"

    def main(self, page: ft.Page):
        page.title = "Habit Tracker"
        page.theme_mode = "light"
        page.window_width = 1000
        page.window_height = 800

        # Define the habits list container
        habits_list = ft.Column(spacing=10)

        def update_habit_list():
            """Update the habit list with Edit and Delete buttons."""
            habits_list.controls.clear()
            for i, habit in enumerate(self.habits):
                habits_list.controls.append(
                    ft.Card(
                        elevation=5,
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        f"Habit: {habit['name']}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(f"Frequency: {habit['frequency']}", size=14),
                                    ft.Text(
                                        f"Target: {habit['target']['amount']} {habit['target']['unit']}",
                                        size=10,
                                    ),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Edit",
                                                on_click=lambda e, i=i: open_habit_dialog(
                                                    i
                                                ),
                                            ),
                                            ft.ElevatedButton(
                                                "Delete",
                                                on_click=lambda e, i=i: delete_habit(i),
                                                bgcolor=ft.colors.RED,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ]
                            ),
                            padding=10,
                        ),
                    )
                )
            page.update()

        def delete_habit(index):
            """Delete a habit from the list."""
            del self.habits[index]
            update_habit_list()

        # Define the habit input fields
        habit_input = ft.TextField(label="Enter new habit", width=300)
        frequency_dropdown = ft.Dropdown(
            width=200,
            label="Frequency",
            options=[
                ft.dropdown.Option("Daily"),
                ft.dropdown.Option("Weekly"),
                ft.dropdown.Option("Monthly"),
            ],
        )
        target_input = ft.Row(
            [
                ft.TextField(label="Target amount", width=150, keyboard_type=ft.KeyboardType.NUMBER),
                ft.Dropdown(
                    width=150,
                    label="Unit",
                    options=[
                        ft.dropdown.Option("minutes"),
                        ft.dropdown.Option("times"),
                        ft.dropdown.Option("pages"),
                        ft.dropdown.Option("kilometers"),
                    ],
                ),
            ]
        )

        # Dialog for adding/editing habits
        habit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Habit"),
            content=ft.Column(
                [
                    habit_input,
                    frequency_dropdown,
                    # ft.Text("Set Target", size=16),
                    # target_input,
                ],
                spacing=30,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_habit_dialog()),
                ft.TextButton("Save", on_click=lambda e: save_habit()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def open_habit_dialog(index=None):
            """Open the dialog to add/edit a habit."""
            self.editing_habit_index = index
            if index is not None:
                # Editing an existing habit
                habit = self.habits[index]
                habit_input.value = habit["name"]
                frequency_dropdown.value = habit["frequency"]
                target_input.controls[0].value = habit["target"]["amount"]
                target_input.controls[1].value = habit["target"]["unit"]
                habit_dialog.title = ft.Text("Edit Habit")
            else:
                # Adding a new habit
                habit_input.value = ""
                frequency_dropdown.value = None
                target_input.controls[0].value = ""
                target_input.controls[1].value = ""
                habit_dialog.title = ft.Text("Add New Habit")

            habit_dialog.open = True
            page.update()

        def close_habit_dialog():
            """Close the dialog."""
            habit_dialog.open = False
            page.update()

        def save_habit():
            """Save a new or edited habit."""
            if habit_input.value and frequency_dropdown.value:
                habit = {
                    "name": habit_input.value,
                    "frequency": frequency_dropdown.value,
                    "target": {
                        "amount": target_input.controls[0].value or "0",
                        "unit": target_input.controls[1].value or "times",
                    },
                    "progress": {},
                }
                if self.editing_habit_index is None:
                    # Add new habit
                    self.habits.append(habit)
                else:
                    # Update existing habit
                    self.habits[self.editing_habit_index] = habit
                    self.editing_habit_index = None

                close_habit_dialog()
                update_habit_list()

        # Calendar view
        def create_calendar_view():
            today = datetime.now()
            cal = calendar.monthcalendar(today.year, today.month)
            calendar_grid = ft.Column(spacing=5)

            # Add month and year header
            calendar_header = ft.Text(
                f"{calendar.month_name[today.month]} {today.year}",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            )
            calendar_grid.controls.append(calendar_header)

            # Add weekday headers
            weekday_headers = ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            day,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLACK,
                        ),
                        width=100,
                        height=40,
                        alignment=ft.alignment.center,
                    )
                    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
            calendar_grid.controls.append(weekday_headers)

            # Add day cells
            for week in cal:
                week_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER)
                for day in week:
                    if day == 0:
                        # Empty cell for days outside the current month
                        day_container = ft.Container(
                            width=100,
                            height=100,
                            bgcolor=ft.colors.GREY_300,
                            border_radius=5,
                            alignment=ft.alignment.center,
                        )
                    else:
                        date_str = f"{today.year}-{today.month:02d}-{day:02d}"

                        # Add tasks for the day with checkboxes
                        habit_indicators = ft.Column()
                        for habit in self.habits:
                            is_done = habit["progress"].get(date_str, False)
                            habit_indicators.controls.append(
                                ft.Checkbox(
                                    label=habit["name"],
                                    value=is_done,
                                    on_change=lambda e, h=habit, d=date_str: toggle_task(
                                        h, d, e.control.value
                                    ),
                                )
                            )

                        day_container = ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(str(day), size=16, weight=ft.FontWeight.BOLD),
                                    habit_indicators,
                                ],
                                spacing=5,
                            ),
                            width=100,
                            height=100,
                            bgcolor=ft.colors.WHITE,
                            border=ft.border.all(1, ft.colors.GREY_400),
                            border_radius=5,
                            alignment=ft.alignment.center,
                        )
                    week_row.controls.append(day_container)
                calendar_grid.controls.append(week_row)

            return ft.Container(
                content=calendar_grid,
                padding=20,
                bgcolor=ft.colors.LIGHT_BLUE_50,
                border_radius=10,
            )

        def toggle_task(habit, date, value):
            """Toggle task completion for a specific day."""
            habit["progress"][date] = value
            page.update()

        # Navigation functions
        def switch_to_calendar(e):
            self.current_page = "calendar"
            page.controls.clear()
            page.controls.extend([create_calendar_view(), back_button])
            page.update()

        def switch_to_habits(e):
            self.current_page = "habits"
            page.controls.clear()
            page.controls.extend([add_habit_button, habits_list, view_calendar_button])
            page.update()

        # Buttons
        add_habit_button = ft.ElevatedButton(
            "Add New Habit", on_click=lambda e: open_habit_dialog(), icon=ft.icons.ADD
        )
        view_calendar_button = ft.ElevatedButton(
            "View Calendar", on_click=switch_to_calendar
        )
        back_button = ft.ElevatedButton("Back to Habits", on_click=switch_to_habits)

        # Main container
        page.add(add_habit_button, habits_list, view_calendar_button)

        # Set the dialog
        page.dialog = habit_dialog

        update_habit_list()


app = HabitTracker()
ft.app(target=app.main)
