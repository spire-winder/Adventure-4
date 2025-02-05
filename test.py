import urwid

def show_new_body(button):
    new_body = urwid.ListBox(urwid.SimpleFocusListWalker([
        urwid.Text("This is the new body!"),
        urwid.Divider(),
        urwid.Button("Go Back", show_original_body)
    ]))
    frame.body = new_body
    loop.widget = frame  # Refresh the UI

def show_original_body(button):
    frame.body = original_body
    loop.widget = frame  # Refresh the UI

# Create initial body
original_body = urwid.ListBox(urwid.SimpleFocusListWalker([
    urwid.Text("Press the button to change the body"),
    urwid.Divider(),
    urwid.Button("Change Body", show_new_body)
]))

# Create the Frame
frame = urwid.Frame(body=original_body)

# Start the UI
loop = urwid.MainLoop(frame, unhandled_input=lambda key: exit() if key in ('q', 'Q') else None)
loop.run()
