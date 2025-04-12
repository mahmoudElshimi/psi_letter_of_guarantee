{
    "name": "Psi Letter of Guarantee",
    "category": "ERP",
    "summary": "Manage Letters of Guarantee",
    "description": "A fully-featured module to manage letters of guarantee in the system.",
    "author": "Mahmoud ElShimi",
    "website": "mailto:mahmoudelshimi@protonmail.ch",
    "depends": ["base", "account", "mail"],
    "license": "Other proprietary",  # See LICENSE(MIT/X) File in the same dir.
    "images": [
        "static/description/banner.png",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/letter_of_guarantee_view.xml",
        "views/menu.xml",
        "report/letter_of_guarantee_report_template.xml",
        "report/psi_letter_of_guarantee_reports.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
