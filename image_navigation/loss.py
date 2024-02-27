
# my custom loss function for image navigation
import numpy as np


def loss_fct(tissue_clusters) -> float:
    print('####################################################')
    print("Calculating loss function:")

    # Presence of landmark tissues:

    # Standard plane has 7 bones, 2 tendons and 1 ulnar cluster
    bones_loss = abs(len(tissue_clusters['bones']) - 7)
    ligament_loss = abs(len(tissue_clusters['tendins']) - 2)
    ulnar_loss = abs(len(tissue_clusters['ulnar']) - 1)

    landmark_loss = bones_loss + ligament_loss + ulnar_loss

    # Absence of landmarks:
    missing_landmark_loss = 0

    # Location of landmarks:
    location_loss = 1

    # There must be bones:
    if len(tissue_clusters['bones'])!=0:
        
        # Get centers of tissue clusters:
        bones_centers = [cluster['center'] for _, cluster in enumerate(tissue_clusters['bones'])]
        bones_centers_mean = np.mean(bones_centers, axis=0)

        # There must be tendins:
        if len(tissue_clusters['tendins'])!=0:

            # Get centers of tissue clusters:
            ligament_centers = [cluster['center'] for _, cluster in enumerate(tissue_clusters['tendins'])]
            ligament_centers_mean = np.mean(ligament_centers, axis=0)

            # Check the orientation of the arm:
            # The bones center might be over or undere the tendins center depending on the origin
            if bones_centers_mean[1] > ligament_centers_mean[1]:
                print("Orientation: bones over tendins")
                orientation = -1
            else: 
                print("Orientation: bones under tendins")
                orientation = 1

            # There must be one ulnar artery:
            if len(tissue_clusters['ulnar'])==1:
                
                # There must be only one ulnar tissue so there is no need to take the mean
                ulnar_center = tissue_clusters['ulnar'][0]['center']

                # Ulnar artery must be over tendins in the positive orientation:
                if orientation * ulnar_center[1] > orientation * ligament_centers_mean[1]: 
                    location_loss = 0
                else: print("Ulnar center not where excpected")
            
            # if no ulnar artery
            else: 
                missing_landmark_loss = 1
                print("No ulnar artery found")
        # if no tendins
        else: 
            missing_landmark_loss = 2
            print("No tendins found")
    # if no bones:
    else: 
        missing_landmark_loss = 3
        print("No bones found")

    # Loss is bounded between 0 and 1
    loss = (1/3)*(0.1*landmark_loss + (1/3)*missing_landmark_loss + location_loss)

    print(f"Landmark loss: {landmark_loss}")
    print(f"Missing landmark loss: {missing_landmark_loss}")
    print(f"Location loss: {location_loss}")
    print(f"Total loss: {loss}")

    print('#################################################### \n')

    return loss