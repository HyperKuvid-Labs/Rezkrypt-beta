import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Video, 
  VideoOff, 
  Mic, 
  MicOff, 
  PhoneOff, 
  Camera,
  Settings,
  Users,
  AlertTriangle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const VideoInterview: React.FC = () => {
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isInCall, setIsInCall] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<'pending' | 'granted' | 'denied' | 'error'>('pending');
  const [isLoading, setIsLoading] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const { toast } = useToast();

  // Request media permissions on component mount
  useEffect(() => {
    requestMediaPermissions();
    return () => {
      // Cleanup stream when component unmounts
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Update video stream when videoRef is available
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const requestMediaPermissions = async () => {
    setIsLoading(true);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      setStream(mediaStream);
      setPermissionStatus('granted');
      setIsInCall(true);
      
      toast({
        title: "Camera and microphone access granted",
        description: "You're ready to start your video interview!",
      });
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      setPermissionStatus('denied');
      
      let errorMessage = "Failed to access camera and microphone";
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = "Camera and microphone access was denied. Please allow permissions and refresh the page.";
        } else if (error.name === 'NotFoundError') {
          errorMessage = "No camera or microphone found on this device.";
        } else if (error.name === 'NotReadableError') {
          errorMessage = "Camera or microphone is already in use by another application.";
        }
      }
      
      toast({
        title: "Media Access Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleVideo = async () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !isVideoEnabled;
        setIsVideoEnabled(!isVideoEnabled);
        
        toast({
          title: isVideoEnabled ? "Camera disabled" : "Camera enabled",
          description: isVideoEnabled ? "Your video is now off" : "Your video is now on",
        });
      }
    }
  };

  const toggleAudio = async () => {
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !isAudioEnabled;
        setIsAudioEnabled(!isAudioEnabled);
        
        toast({
          title: isAudioEnabled ? "Microphone muted" : "Microphone unmuted",
          description: isAudioEnabled ? "Your audio is now muted" : "Your audio is now unmuted",
        });
      }
    }
  };

  const endInterview = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsInCall(false);
    setPermissionStatus('pending');
    
    toast({
      title: "Interview ended",
      description: "Thank you for your time. The interview has been terminated.",
    });
  };

  const retryPermissions = () => {
    setPermissionStatus('pending');
    requestMediaPermissions();
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Video Interview</h1>
          <p className="text-muted-foreground">
            Connect with candidates and employers through our secure video platform
          </p>
        </div>

        {/* Main Video Area */}
        <Card className="shadow-xl">
          <CardContent className="p-0">
            <div className="relative aspect-video bg-accent/20 rounded-t-xl overflow-hidden">
              {/* Permission Status & Loading */}
              {permissionStatus === 'pending' && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/90 z-10">
                  <div className="text-center space-y-4">
                    {isLoading ? (
                      <>
                        <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
                        <p className="text-foreground font-medium">Requesting camera and microphone access...</p>
                        <p className="text-muted-foreground text-sm">Please allow permissions in your browser</p>
                      </>
                    ) : (
                      <>
                        <Camera className="w-16 h-16 text-muted-foreground mx-auto" />
                        <p className="text-foreground font-medium">Camera access required</p>
                        <Button onClick={requestMediaPermissions} className="gap-2">
                          <Camera className="w-4 h-4" />
                          Request Permissions
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Permission Denied State */}
              {permissionStatus === 'denied' && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/90 z-10">
                  <div className="text-center space-y-4 max-w-md">
                    <AlertTriangle className="w-16 h-16 text-destructive mx-auto" />
                    <h3 className="text-lg font-semibold text-foreground">Camera Access Denied</h3>
                    <p className="text-muted-foreground text-sm">
                      Please enable camera and microphone permissions for this site in your browser settings, then try again.
                    </p>
                    <div className="space-y-2">
                      <Button onClick={retryPermissions} className="gap-2">
                        <Camera className="w-4 h-4" />
                        Try Again
                      </Button>
                      <p className="text-xs text-muted-foreground">
                        Look for the camera icon in your browser's address bar
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Main Video Feed */}
              <div className="absolute inset-0">
                {permissionStatus === 'granted' && stream ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                    style={{ 
                      transform: 'scaleX(-1)', // Mirror the video like a selfie
                      display: isVideoEnabled ? 'block' : 'none'
                    }}
                  />
                ) : null}
                
                {/* Video disabled overlay */}
                {!isVideoEnabled && permissionStatus === 'granted' && (
                  <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                    <div className="text-center space-y-4">
                      <VideoOff className="w-16 h-16 text-white/60 mx-auto" />
                      <p className="text-white/80 text-lg">Camera is disabled</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Remote Participant Video (Picture-in-Picture) */}
              <div className="absolute top-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <Users className="w-8 h-8 text-white/60 mx-auto" />
                    <p className="text-xs text-white/80">Remote participant</p>
                  </div>
                </div>
              </div>

              {/* Interview Status */}
              <div className="absolute top-4 left-4">
                <div className="flex items-center gap-2 bg-black/20 backdrop-blur-sm rounded-lg px-3 py-2">
                  <div className={`w-2 h-2 rounded-full ${isInCall ? 'bg-red-500' : 'bg-green-500'}`}></div>
                  <span className="text-white text-sm font-medium">
                    {isInCall ? 'Recording' : 'Ready to Connect'}
                  </span>
                </div>
              </div>

              {/* Video Controls Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-6">
                <div className="flex items-center justify-center gap-4">
                  {/* Microphone Toggle */}
                  <Button
                    size="icon"
                    variant={isAudioEnabled ? "secondary" : "destructive"}
                    onClick={toggleAudio}
                    className="h-12 w-12 rounded-full"
                  >
                    {isAudioEnabled ? (
                      <Mic className="w-5 h-5" />
                    ) : (
                      <MicOff className="w-5 h-5" />
                    )}
                  </Button>

                  {/* End Interview Button */}
                  <Button
                    size="lg"
                    variant="destructive"
                    onClick={endInterview}
                    className="h-12 px-8 rounded-full gap-2 font-semibold"
                  >
                    <PhoneOff className="w-5 h-5" />
                    End Interview
                  </Button>

                  {/* Video Toggle */}
                  <Button
                    size="icon"
                    variant={isVideoEnabled ? "secondary" : "destructive"}
                    onClick={toggleVideo}
                    className="h-12 w-12 rounded-full"
                  >
                    {isVideoEnabled ? (
                      <Video className="w-5 h-5" />
                    ) : (
                      <VideoOff className="w-5 h-5" />
                    )}
                  </Button>

                  {/* Settings */}
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-12 w-12 rounded-full text-white hover:bg-white/20"
                  >
                    <Settings className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Interview Information Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interview Details */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Interview Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-muted-foreground">Position</p>
                  <p className="text-foreground">Senior Software Engineer</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Company</p>
                  <p className="text-foreground">TechCorp Inc.</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Interviewer</p>
                  <p className="text-foreground">Sarah Johnson</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Duration</p>
                  <p className="text-foreground">45 minutes</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <p className="font-medium text-muted-foreground">Interview Focus</p>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs">
                    Technical Skills
                  </span>
                  <span className="bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs">
                    Problem Solving
                  </span>
                  <span className="bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs">
                    Team Collaboration
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start gap-2">
                <Settings className="w-4 h-4" />
                Audio/Video Settings
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2">
                <Users className="w-4 h-4" />
                Invite Participant
              </Button>
              <div className="pt-2 border-t border-border">
                <p className="text-xs text-muted-foreground mb-2">
                  Connection Status
                </p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Excellent Connection</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Technical Notes */}
        <Card className="bg-accent/10 border-accent/20">
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-2">
              Implementation Notes
            </h3>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>• This is a UI mockup for the video interview feature</p>
              <p>• In production, integrate with WebRTC (Agora, Twilio, or custom solution)</p>
              <p>• Add real-time recording, screen sharing, and chat capabilities</p>
              <p>• Implement participant management and interview scheduling</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VideoInterview;