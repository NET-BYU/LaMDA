# LaMDA: Location and Movement Detection at the Application layer

Community-driven sensor networks have been instrumental in providing easy access to affordable, large-scale measurement recording. This boom is facilitated by the accessibility of inexpensive sensor hardware. Unfortunately, the simplicity of this hardware makes it challenging to retrieve trustworthy location data without added hardware such as GPS. In this paper, we introduce the LaMDA framework: a software-based solution run solely in a web browser to determine the location of a sensor with the aid of a registering device equipped with positioning hardware such as a phone or laptop. After verifying the proximity of the sensor to the registering device we monitor the sensor for any possible location changes by employing an algorithm that analyzes its `traceroute` behavior from the perspective of a central server. This solution allows minimal firmware changes to be made to fleets of sensors without recall or changes to hardware and a simple piece of software to run alongside an existing central server.
