### Version Collector: An NVDA Add-on

This is an [NVDA][1] add-on, designed to collect the name and version numbers of any software the user runs.
This process is completely passive to the user.
As long as the add-on is enabled, it will collect version info.

A list of all installed NVDA add-ons is also collected.

Currently, each time you restart NVDA, the collected data is lost.
A file-backed listing is intended for a future version.

### Controls

To view a tabular list of applications and add-ons which Version Collector has encountered, press `NVDA+ctrl+shift+v`.
You may change this key mapping under the **Tools** category of NVDA's Input Gestures dialog--search for "Version Collector".

You can browse the version report like a webpage, with two tables.
The first table is applications which have been the focused window while the add-on was running.
The second table is the list of NVDA add-ons.
You may select any or all of these items using normal Windows or NVDA commands, and copy them to the clipboard.
You can exit the report view by pressing escape.

As an alternative to viewing the report, if your objective is to copy the entire list of detected versions to the clipboard, you may instead press the `NVDA+shift+ctrl+v` key sequence twice rapidly.
In this case, a text formatted report will be copied directly to the clipboard without ever opening the report viewer.

### Special notes

* In order to collect your NVDA version, you may simply open the NVDA menu (`NVDA+n`). This is enough to include your NVDA version in the list of captured versions. A future release will collect your NVDA version without needing to do this.
* In order to collect your Windows version, open any Windows application (Explorer, desktop, etc.), and reference the version column that appears in the report. The Windows version will be directly collected in a future version.

Please make feature requests by email or [GitHub issue][2].
As always, I am happy to hear from users of my add-ons, even just to say how you found the add-on useful.

[1]: https://nvaccess.org/
[2]: https://github.com/opensourcesys/versionCollector
