import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Clock, GitBranch, GitCommit, User, Calendar } from "lucide-react";

interface DeploymentInfo {
  status: "success" | "failure" | "pending";
  commit: string;
  branch: string;
  author: string;
  message: string;
  timestamp: string;
  server: string;
}

export default function DeploymentStatus() {
  const [deployments, setDeployments] = useState<DeploymentInfo[]>([
    {
      status: "success",
      commit: "abbd3c1",
      branch: "main",
      author: "Manus Deploy",
      message: "feat: Add PM2 auto-restart and Telegram deployment notifications",
      timestamp: new Date().toISOString(),
      server: "13.113.194.218"
    }
  ]);

  const getStatusIcon = (status: DeploymentInfo["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "failure":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />;
    }
  };

  const getStatusBadge = (status: DeploymentInfo["status"]) => {
    const variants = {
      success: "default" as const,
      failure: "destructive" as const,
      pending: "secondary" as const
    };
    return (
      <Badge variant={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Deployment Status</h1>
          <p className="text-muted-foreground">
            Monitor GitHub Actions deployment history and status
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Deployments</CardTitle>
            <CardDescription>
              Latest deployments from GitHub Actions to Windows Server
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {deployments.map((deployment, index) => (
                <Card key={index} className="border-l-4 border-l-primary">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="space-y-3 flex-1">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(deployment.status)}
                          <span className="font-semibold text-lg">
                            {deployment.message}
                          </span>
                          {getStatusBadge(deployment.status)}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <GitBranch className="h-4 w-4" />
                            <span>Branch: <code className="px-1 py-0.5 bg-muted rounded">{deployment.branch}</code></span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <GitCommit className="h-4 w-4" />
                            <span>Commit: <code className="px-1 py-0.5 bg-muted rounded">{deployment.commit}</code></span>
                          </div>

                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4" />
                            <span>Author: {deployment.author}</span>
                          </div>

                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>Time: {new Date(deployment.timestamp).toLocaleString()}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-muted-foreground">Server:</span>
                          <code className="px-2 py-1 bg-muted rounded">{deployment.server}</code>
                        </div>
                      </div>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open("https://github.com/ripgtxgt/trading_dashboard/actions", "_blank")}
                      >
                        View Logs
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-6 flex justify-center">
              <Button
                variant="outline"
                onClick={() => window.open("https://github.com/ripgtxgt/trading_dashboard/actions", "_blank")}
              >
                View All Deployments on GitHub
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Deployment Configuration</CardTitle>
            <CardDescription>
              Current deployment settings and information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Repository</label>
                  <div className="mt-1 p-2 bg-muted rounded">
                    <code>ripgtxgt/trading_dashboard</code>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Target Server</label>
                  <div className="mt-1 p-2 bg-muted rounded">
                    <code>13.113.194.218</code>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Deploy Path</label>
                  <div className="mt-1 p-2 bg-muted rounded">
                    <code>C:\trading_dashboard_fixed</code>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Telegram Notifications</label>
                  <div className="mt-1 p-2 bg-muted rounded flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span>Enabled</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">Deployment Process</h4>
                <ol className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="font-mono">1.</span>
                    <span>Code pushed to GitHub main branch</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">2.</span>
                    <span>GitHub Actions triggered automatically</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">3.</span>
                    <span>SSH connection to Windows Server</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">4.</span>
                    <span>Pull latest code from GitHub</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">5.</span>
                    <span>Install dependencies and build project</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">6.</span>
                    <span>Restart PM2 services</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono">7.</span>
                    <span>Send Telegram notification</span>
                  </li>
                </ol>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
