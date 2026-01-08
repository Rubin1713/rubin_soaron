import 'package:flutter/material.dart';
import 'package:rc_app/widgets/video_stream.dart';

class HomeLayout extends StatefulWidget {
  final Widget? topLeft;
  final Widget? topCenter;
  final Widget? topRight;
  final Widget? bottomLeft;
  final Widget? bottomCenter;
  final Widget? bottomRight;
  final Widget? center;
  final bool showVideoStream;

  const HomeLayout({
    Key? key,
    this.showVideoStream = false,
    this.topLeft = const SizedBox(),
    this.topCenter = const SizedBox(),
    this.topRight = const SizedBox(),
    this.center = const SizedBox(),
    this.bottomLeft = const SizedBox(),
    this.bottomCenter = const SizedBox(),
    this.bottomRight = const SizedBox(),
  }) : super(key: key);

  @override
  State<HomeLayout> createState() => HomeLayoutState();
}

class HomeLayoutState extends State<HomeLayout> {
  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // ================= BACKGROUND VIDEO =================
        Positioned.fill(
          child: widget.showVideoStream
              ? const VideoStream()
              : const SizedBox(),
        ),

        // ================= UI OVERLAY =================
        Padding(
          padding: const EdgeInsets.all(30),
          child: Column(
            children: [
              // =================================================
              // TOP SECTION (Telemetry / Mode / Attitude)
              // =================================================
             Expanded(
  		flex: 4, // ⬅️ give more vertical space
	  child: Row(
	    crossAxisAlignment: CrossAxisAlignment.start,
	    children: [
	      Expanded(
	        flex: 2,
	        child: Padding(
	          padding: const EdgeInsets.only(bottom: 12), // ⬅️ key fix
	          child: widget.topLeft!,
	        ),
	      ),
	
	      Expanded(
	        flex: 1,
	        child: Column(
	          children: [
	            const SizedBox(height: 40),
	            widget.topCenter!,
	          ],
	        ),
	      ),
	
	      Expanded(
	        flex: 2,
	        child: Align(
	          alignment: Alignment.topRight,
	          child: widget.topRight!,
	        ),
	      ),
	    ],
	  ),
	),


              // =================================================
              // CENTER STATUS (Scanning / Messages)
              // =================================================
              if (widget.center != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  child: widget.center!,
                ),

              // =================================================
              // BOTTOM SECTION (Controls)
              // =================================================
              Expanded(
                flex: 2,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    // -------- BOTTOM LEFT --------
                    Expanded(
                      child: Align(
                        alignment: Alignment.bottomLeft,
                        child: widget.bottomLeft!,
                      ),
                    ),

                    // -------- BOTTOM CENTER --------
                    Expanded(
                      child: Align(
                        alignment: Alignment.bottomCenter,
                        child: widget.bottomCenter!,
                      ),
                    ),

                    // -------- BOTTOM RIGHT --------
                    Expanded(
                      child: Align(
                        alignment: Alignment.bottomRight,
                        child: widget.bottomRight!,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

