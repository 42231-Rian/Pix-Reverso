[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Title = "Pix Reverso",

    [Parameter(Mandatory=$false)]
    [string]$Message = "Você acabou de pagar para se arrepender.",

    [Parameter(Mandatory=$false)]
    [string]$Subtext = "Banco Central do Arrependimento"
)

# Ensure UTF-8 output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    # Escape XML entities
    $safeTitle = [System.Security.SecurityElement]::Escape($Title)
    $safeMessage = [System.Security.SecurityElement]::Escape($Message)
    $safeSubtext = [System.Security.SecurityElement]::Escape($Subtext)

    $toastXmlString = @"
<toast duration="long">
    <visual>
        <binding template="ToastGeneric">
            <text>$safeTitle</text>
            <text>$safeMessage</text>
            <text>$safeSubtext</text>
        </binding>
    </visual>
    <audio src="ms-winsoundevent:Notification.Reminder"/>
</toast>
"@

    $xmlDoc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xmlDoc.LoadXml($toastXmlString)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xmlDoc)
    
    # App ID
    $appId = "Pix Reverso"
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
    Write-Output "OK"
}
catch {
    Write-Error $_.Exception.Message
}
