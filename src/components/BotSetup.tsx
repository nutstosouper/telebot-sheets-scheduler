
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const BotSetup = () => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Telegram Bot Setup</CardTitle>
          <CardDescription>
            How to create and set up your Telegram bot
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ol className="list-decimal list-inside space-y-3">
            <li className="text-gray-700">
              <span className="font-medium">Create a new bot with BotFather</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                Open Telegram and search for @BotFather. Start a chat and use the /newbot command to create a new bot.
                Follow the instructions to set a name and username for your bot.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Get your bot token</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                BotFather will provide you with a token. This token is required to authorize your bot and send requests to the Telegram Bot API.
              </p>
            </li>
            <li className="text-gray-700">
              <span className="font-medium">Set up environment variables</span>
              <p className="text-sm text-gray-600 ml-6 mt-1">
                Store your bot token securely in environment variables.
              </p>
            </li>
          </ol>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Important</AlertTitle>
            <AlertDescription>
              Keep your bot token secret. Never share it or commit it to public repositories.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Required Python Packages</CardTitle>
          <CardDescription>
            Install these packages to develop your Telegram bot
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-md font-mono text-sm relative">
            <pre>pip install aiogram gspread oauth2client python-dotenv</pre>
            <Button 
              variant="ghost" 
              size="icon" 
              className="absolute top-2 right-2 h-6 w-6 text-gray-400 hover:text-white"
              onClick={() => handleCopy("pip install aiogram gspread oauth2client python-dotenv")}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          {copied && <p className="text-green-500 text-xs mt-1">Copied to clipboard!</p>}
        </CardContent>
      </Card>
    </div>
  );
};

export default BotSetup;
