import json
import math
from collections import OrderedDict
from operator import getitem
import player_lookup

master_dictionary = {}
best_points = {1: [],2: [],3: [],4: [],5: [],6: [],7: [],8: [],9: []}

def calculate_packle_points(file,game):
    local_dictionary = {}
    #1 load json as dictionary
    json_file = open(file)
    json_data = json.load(json_file)

    #2 add players name id and primary time to a local dictionary
    for i in json_data["data"]["runs"]:
        #if player doesnt have a speedrun.com account add there guest name to the local dictionary
        if i["run"]["players"][0]["rel"] == "guest":
            #match sure players fastest time is used, thps1 has two times for zen_ivan for example
            if i["run"]["players"][0]["name"] not in local_dictionary:
                local_dictionary[i["run"]["players"][0]["name"]] = {"nameid": i["run"]["players"][0]["name"], "primaryt": i["run"]["times"]["primary_t"], "ppoints": 0}
        #if player does have a speedrun.com account add there profile id to the local dictionary
        else:
            #match sure players fastest time is used, thps1 has two times for zen_ivan for example
            if i["run"]["players"][0]["id"] not in local_dictionary:
                local_dictionary[i["run"]["players"][0]["id"]] = {"nameid": i["run"]["players"][0]["id"], "primaryt": i["run"]["times"]["primary_t"], "ppoints": 0}

    #3 calculate packle points
    #find the fastest time (it will always be the first run it finds as speedrun already orders runs fastest to slowest)
    fastest_time = 999999999
    for v in local_dictionary.values():
        if v["primaryt"] < fastest_time:
            fastest_time = v["primaryt"]
    
    #calculate the points!
    for v in local_dictionary.values():
        v["ppoints"] = math.floor((0.008 * pow(math.e,(4.8284*(fastest_time/v["primaryt"]))))*1000)

    #save the top 3 scores to use for coloring the grid later
    j = 0
    for v in local_dictionary.values():
        best_points[game].append(v["ppoints"])
        j += 1
        if j == 3:
            break

    #4 push local dictionary to master dictionary if player doesnt already excist in database
    for v in local_dictionary.values():
        #if player is not in dictionary
        if v["nameid"] not in master_dictionary:
            master_dictionary[v["nameid"]] = {1: 0,2: 0,3: 0,4: 0,5: 0,6: 0,7: 0,8: 0,9: 0,"tot": 0,"place": 0}
        #add packle points
        master_dictionary[v["nameid"]][game] = v["ppoints"]

    #5 debug
    #print(fastest_time)
    #for i in local_dictionary.values():
        #print(str(i))

#calculate for each leaderboard
calculate_packle_points("thps1.json", 1)
calculate_packle_points("thps2.json", 2)
calculate_packle_points("thps3.json", 3)
calculate_packle_points("thps4.json", 4)
calculate_packle_points("thug.json", 5)
calculate_packle_points("thug2.json", 6)
calculate_packle_points("thaw.json", 7)
calculate_packle_points("thp8.json", 8)
calculate_packle_points("thpg.json", 9)

#change nameids to human readable usernames
for k, v in player_lookup.players.items():
    master_dictionary[v] = master_dictionary.pop(k)

#add up all packle points
for v in master_dictionary.values():
    v["tot"] = v[1]+v[2]+v[3]+v[4]+v[5]+v[6]+v[7]+v[8]+v[9]

#order from most points to lest
sorted_master_dictionary = OrderedDict(sorted(master_dictionary.items(), key = lambda x: getitem(x[1], 'tot'), reverse=True))

#give place numbers!
place_to_give = 0
pause_place = 0
current_ppoints = 99999999999999
for v in sorted_master_dictionary.values():
    if v["tot"] < current_ppoints:
        current_ppoints = v["tot"]
        place_to_give += 1+pause_place
        pause_place = 0
    elif v["tot"] == current_ppoints:
        pause_place += 1
    v["place"] = place_to_give

#proven ground has only 1 runner this breaks stuff so jank fix
best_points[9].append(999999999)
best_points[9].append(999999999)

#print html
for k, v in sorted_master_dictionary.items():
    #color place column
    if v['place'] == 1:
        color = "gold"
    elif v['place'] == 2:
        color = "silver"
    elif v['place'] == 3:
        color = "brown"
    else:
        color = "wheat"

    #build output
    html_line = ""
    html_line += "<tr style='background-color: whitesmoke;'><td style='background-color: "+color+"'>"+str(v['place'])+"</td><td style='background-color: darkgrey;'>"+k+"</td>"
    for i in range(1, 10):
        class_to_use = ""
        if v[i] == best_points[i][0]:
            class_to_use = "gold"
        elif v[i] == best_points[i][1]:
            class_to_use = "silver"
        elif v[i] == best_points[i][2]:
            class_to_use = "bronze"
        elif v[i] == 0:
            class_to_use = "black"
        #print(str(v[1])+":"+str(best_points[i][0]))
        html_line += "<td class='"+class_to_use+"'>"+str(v[i])+"</td>"

    html_line += "<td style='background-color: orange;'><b>"+str(v["tot"])+"</b></td></tr>"
    print(html_line)