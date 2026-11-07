# Sims 2 Sound Package Builder
An app to turn a folder of .mp3 or .xa files into a Sims 2 package, complete with audio initialiser.

## About This Project
To use an audio track in The Sims 2, it must be added to a Sims 2 .package file with an audio initialiser. For the game to be able to find the track, it must be labelled with two instance numbers, created by hashing the file name with two different CRC checksums. Generating those manually for all the sound effects and voice lines I wanted to use in my creations was getting to be a bit of a pain, so I made this program.

## Getting Started
1. Download the Windows or Ubuntu version of the app from the [Releases](https://github.com/MorePopcornSims/Sims2SoundPackageBuilder/releases) page of this repository.
2. Unzip the folder wherever you'd like to save it. No install required!
3. Run the program. You'll be warned that the software isn't signed. If you trust me (and the code you can see here in GitHub) then allow it to run anyway.

## Usage
First, make sure you have named all your audio files the way you want to refer to them in your #STR or ANIM resources. I have some [notes on my Tumblr blog](https://morepopcorn.tumblr.com/post/831938004090339328/sims-2-voice-audio-notes) about the required naming convention for voice lines.

Then open the program. You should find it intuitive to use. The status bar at the bottom of the window will let you know what is going on.

<div align="center"><img src="https://64.media.tumblr.com/0f2b7d91e4dcfae23a1809d98f1f7666/ba31e64d7ac4c756-04/s1280x1920/b37e98c4f5bb3bab1bf1be1d4a8d2563569071af.pnj" width="700"/></div>

Click the 'Select Folder' button to select the folder of audio files. If you've organised them into subfolders, you can click the checkbox so the program reads them all. Once you have selected a valid folder, the file list will update and the 'Save Package' button will activate. Click it to open a 'Save as...' dialogue and choose the name for your package. You will be warned if you are going to overwrite an existing package.

That's it! You can now open your package in SimPE and merge it with another package if you like.
