# TODO: make a prompt texts 
# TODO: request AOAI to generate a ARM template
def generate_arm_template(url: str) -> str:
    return """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": [
            {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2021-04-01",
            "name": "[parameters('storageAccountName')]",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "StorageV2",
            "properties": {}
            }
        ],
        "parameters": {
            "storageAccountName": {
            "type": "string",
            "metadata": {
                "description": "The name of the storage account"
            }
            }
        }
    }
    """