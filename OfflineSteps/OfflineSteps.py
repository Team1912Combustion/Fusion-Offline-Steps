import adsk.core, adsk.fusion, traceback

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        global app
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # define the toolbar button
        main_button = app.userInterface.commandDefinitions.addButtonDefinition(
            'OfflineStepsAddInButton',
            'Import Offline STEPs',
            'Imports STEP files as components without uploading them.',
            './'
        )
        
        # Connect to the command created event.
        sampleCommandCreated = CommandCreatedHandler()
        main_button.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # add the toolbar button to the "Insert" panel
        app.userInterface.allToolbarPanels.itemById('InsertPanel').controls \
            .addCommand(main_button)

        app.userInterface.allToolbarPanels.itemById('CAMManagePanel').controls \
            .addCommand(main_button)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# CommandCreatedEventHandler
class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        file_dialog = app.userInterface.createFileDialog()
        file_dialog.isMultiSelectEnabled = True
        file_dialog.filter = 'STEP Files (*.step;*.stp)'

        if file_dialog.showOpen() != adsk.core.DialogResults.DialogOK: return

        app.userInterface.workspaces.itemById('FusionSolidEnvironment') \
            .activate()

        for file_path in file_dialog.filenames:
            design = adsk.fusion.Design.cast(app.activeProduct)
        
            step_options = app.importManager.createSTEPImportOptions(file_path)
            step_options.isViewFit = False

            if design.designIntent:
                app.importManager.importToTarget(
                    step_options,
                    design.rootComponent
                )
            else: app.importManager.importToNewDocument(step_options)

def remove_button_from_panel(panel_name):
    button = app.userInterface.allToolbarPanels.itemById(panel_name) \
        .controls.itemById('OfflineStepsAddInButton')
    if button: button.deleteMe()

def stop(context):
    try:
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('OfflineStepsAddInButton')
        if cmdDef:
            cmdDef.deleteMe()

        remove_button_from_panel('InsertPanel')
        remove_button_from_panel('CAMManagePanel')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	
