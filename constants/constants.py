TASK_STATUS = {
    'TODO': 1,
    'IN_PROGRESS': 2,
    'VERIFY': 3,
    'CORECTION': 4,
    'COMPLETE': 5
}

PROJECT_STATUS = {
    'ACTIVE': 1,
    'INACTIVE': 2,
    'COMPLETED': 3,
    'HOLD': 4,
    'CANCELLED': 5,
    'ALL': 6
}

ROLE = {
    'LEAD': 1,
    'MANAGER': 2,
    'PEER': 3,
}

INACTIVE = 'inactive'
ALL = 'all'

PEER = 'peer'
LEAD = 'lead'
MANAGER = 'manager'

TASK_TODO = 'TODO'
TASK_PROGRESS = 'IN-PROGRESS'
TASK_VERIFY = 'VERIFY'
TASK_CORRECTION = 'CORRECTION'
TASK_HOLD = 'HOLD'
TASK_COMPLETE = 'COMPLETE'
TASK_ALL = 'ALL'

MAILCONFIGURE = 'MAILCONFIGURE'

ADMIN_NAV = {
    'Dashboard': 'admin-dashboard',
    'View Projects': 'view-projects',
    'View Tasks': 'view-tasks',
    'View Members': 'view-members',
    'Mail Server': 'mail-server',
}

LEAD_NAV = {
    'Dashboard': 'lead',
    'View Projects': 'view-projects',
    'View Tasks': 'view-tasks',
    'View Members': 'view-members',
    'Mail Server': 'mail-server',
}

MANAGER_NAV = {
    'Dashboard': 'manager',
    'View Projects': 'view-projects',
    'View Tasks': 'view-tasks',
    'View Members': 'view-members',
}

PEER_NAV = {
    'Dashboard': 'peer',
    'View Projects': 'view-projects',
    'View Tasks': 'view-tasks',
    'View Members': 'view-members',
}


def task_mail_context(task, user_name):
    subject = f'New Task'
    message = f'''
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .email-container {{
                background-color: #fff;
                margin: 20px auto;
                padding: 20px;
                max-width: 600px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                background-color: #004085;
                color: white;
                padding: 10px 0;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                padding: 20px;
                line-height: 1.6;
            }}
            .highlight {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .task-details {{
                background-color: #f8f9fa;
                border-left: 4px solid #004085;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .task-details td {{
                padding: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">Bliss-InfoTech New Task</div>
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>Hope you're doing well. You have been assigned with a new task. The details are mentioned below, and we kindly ask you to complete it by on or before <span class="highlight">{task.due}</span>.</p>
                <div class="task-details">
                    <table>
                        <tr><td>Task Name:</td><td>{task.name}</td></tr>
                        <tr><td>Task ID:</td><td>{task.id}</td></tr>
                        <tr><td>Project:</td><td>{task.project.name}</td></tr>
                        <tr><td>Due Date:</td><td>{task.due}</td></tr>
                    </table>
                </div>
                <p>Best Regards,</p>
                <p><strong>Bliss-InfoTech</strong></p>
            </div>
            <div class="footer">
                <p>If any query please contact blissinfotech.query@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return {"subject": subject, "message": message}

def test_mail_context():
    subject = 'Project Manager Test Mail'
    message = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Mail</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333333;
                text-align: center;
            }
            p {
                color: #555555;
                line-height: 1.5;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #888888;
            }
            .highlight {
                background-color: #e7f0ff;
                padding: 10px;
                border-left: 4px solid #007bff;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bliss-InfoTech</h1>
            <div class="highlight">
                <p>This is a test mail from <strong>Bliss-Infotech Task Manager</strong>.</p>
            </div>
            <p>Thank you for being a part of our community! If you have any questions, feel free to reach out to us.</p>
            <div class="footer">
                <p>Best Regards,<br>Bliss-InfoTech Team</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return {"subject": subject, "message": message}

def project_assigned_mail_context(project, manager_name):
    subject = f'New Project'
    message = f'''
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .email-container {{
                background-color: #fff;
                margin: 20px auto;
                padding: 20px;
                max-width: 600px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                background-color: #004085;
                color: white;
                padding: 10px 0;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                padding: 20px;
                line-height: 1.6;
            }}
            .highlight {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .task-details {{
                background-color: #f8f9fa;
                border-left: 4px solid #004085;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .task-details td {{
                padding: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">Bliss-InfoTech New Project - {project.name}</div>
            <div class="content">
                <p>Greetings <strong>{manager_name}</strong>,</p>
                <p> hope this message finds you well.<br>We are happy to inform that you have been assigned as the project manager for the {project.name}. This project is a high priority and aligns with our Bliss-Infotech strategic goals. I have full confidence in your ability to lead the team and deliver exceptional results.</span>.</p>
                <div class="task-details">
                    <h4>Here are some key details of the project:</h4>
                    <table>
                        <tr><td>Project Name:</td><td>{project.name}</td></tr>
                        <tr><td>Project ID:</td><td>{project.id}</td></tr>
                        <tr><td>Start Date:</td><td>{project.started}</td></tr>
                        <tr><td>Planned Completion Date:</td><td>{project.due}</td></tr>
                    </table>
                </div>
                <p>Best Regards,</p>
                <p><strong>Bliss-InfoTech</strong></p>
            </div>
            <div class="footer">
                <p>If any query please contact blissinfotech.query@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return {"subject": subject, "message": message}