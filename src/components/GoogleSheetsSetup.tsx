
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Separator } from "@/components/ui/separator";

const GoogleSheetsSetup = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Google Sheets API Setup</CardTitle>
          <CardDescription>
            How to connect your bot to Google Sheets
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ol className="list-decimal list-inside space-y-3">
            <li className="text-gray-700">
              <span className="font-medium">Create a Google Cloud Project</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                Go to the <a href="https://console.cloud.google.com/" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Google Cloud Console</a> and create a new project.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Enable the Google Sheets API</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                In your project, navigate to "APIs & Services" > "Library" and enable the Google Sheets API.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Create Service Account Credentials</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                Go to "APIs & Services" > "Credentials", click "Create credentials" and select "Service account". 
                Follow the instructions to create a service account.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Generate JSON Key</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                After creating the service account, click on it, go to the "Keys" tab, and create a new key in JSON format. Download this file.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Share your Google Sheet</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                Create a new Google Sheet or use an existing one, and share it with the email address of your service account (found in the JSON file) with Editor permissions.
              </p>
            </li>
          </ol>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Important</AlertTitle>
            <AlertDescription>
              Keep your JSON credentials file secure and never share it publicly.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Sheet Structure</CardTitle>
          <CardDescription>
            How to organize your Google Sheets for the bot
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-800 mb-2">Services Sheet</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white rounded-md border">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="py-2 px-4 border-b">Service ID</th>
                      <th className="py-2 px-4 border-b">Name</th>
                      <th className="py-2 px-4 border-b">Description</th>
                      <th className="py-2 px-4 border-b">Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-2 px-4 border-b">1</td>
                      <td className="py-2 px-4 border-b">Service A</td>
                      <td className="py-2 px-4 border-b">Description of Service A</td>
                      <td className="py-2 px-4 border-b">100</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium text-gray-800 mb-2">Clients Sheet</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white rounded-md border">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="py-2 px-4 border-b">User ID</th>
                      <th className="py-2 px-4 border-b">Username</th>
                      <th className="py-2 px-4 border-b">Full Name</th>
                      <th className="py-2 px-4 border-b">Role</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-2 px-4 border-b">123456789</td>
                      <td className="py-2 px-4 border-b">john_doe</td>
                      <td className="py-2 px-4 border-b">John Doe</td>
                      <td className="py-2 px-4 border-b">client</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium text-gray-800 mb-2">Appointments Sheet</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white rounded-md border">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="py-2 px-4 border-b">Appointment ID</th>
                      <th className="py-2 px-4 border-b">User ID</th>
                      <th className="py-2 px-4 border-b">Service ID</th>
                      <th className="py-2 px-4 border-b">Date</th>
                      <th className="py-2 px-4 border-b">Time</th>
                      <th className="py-2 px-4 border-b">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-2 px-4 border-b">1</td>
                      <td className="py-2 px-4 border-b">123456789</td>
                      <td className="py-2 px-4 border-b">1</td>
                      <td className="py-2 px-4 border-b">2025-04-20</td>
                      <td className="py-2 px-4 border-b">14:00</td>
                      <td className="py-2 px-4 border-b">confirmed</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GoogleSheetsSetup;
