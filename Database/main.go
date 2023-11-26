package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"
)

type LessonData struct {
	Number   int    `json:"number"`
	Type     string `json:"type"`
	Name     string `json:"name"`
	Teacher  string `json:"teacher"`
	Location string `json:"location"`
	Comment  string `json:"comment"`
}

var weekDays map[string]int
var sheduleCall []int
var groups []string

func main() {
	groups = []string{"ПИ-б-о-231(1)", "ПИ-б-о-231(2)", "ПИ-б-о-232(1)", "ПИ-б-о-232(2)", "ПИ-б-о-233(1)", "ПИ-б-о-233(2)",
		"ИВТ-б-о-231(1)", "ИВТ-б-о-231(2)", "ИВТ-б-о-232(1)", "ИВТ-б-о-232(2)"}
	weekDays = make(map[string]int)
	weekDays["Понедельник"] = 0
	weekDays["Вторник"] = 1
	weekDays["Среда"] = 2
	weekDays["Четверг"] = 3
	weekDays["Пятница"] = 4
	weekDays["Суббота"] = 5
	weekDays["Воскресенье"] = 6
	sheduleCall = []int{480, 590, 690, 800, 900, 1000, 1100, 1440}
	http.HandleFunc("/getshedule", GetSheduleHandler)
	http.ListenAndServe(":8050", nil)
}

func GetSheduleHandler(w http.ResponseWriter, r *http.Request) {
	var result []byte
	command := r.URL.Query().Get("command")

	if command == "nextlesson" {
		group := r.URL.Query().Get("group")
		fullname := r.URL.Query().Get("fullname")
		answer, number := NextLesson(group, fullname)
		var ans struct {
			Number   int    `json:"number"`
			Type     string `json:"type"`
			Name     string `json:"name"`
			Teacher  string `json:"teacher"`
			Location string `json:"location"`
			Comment  string `json:"comment"`
			Hours    string `json:"hours"`
			Minutes  string `json:"minutes"`
		}
		ans.Number = answer.Number
		ans.Type = answer.Type
		ans.Name = answer.Name
		ans.Teacher = answer.Teacher
		ans.Location = answer.Location
		ans.Comment = answer.Comment
		ans.Hours = strconv.Itoa(sheduleCall[number] / 60)
		ans.Minutes = strconv.Itoa(sheduleCall[number] % 60)
		if len(ans.Minutes) < 2 {
			ans.Minutes = "0" + ans.Minutes
		}
		result, _ = json.Marshal(ans)
	}
	if command == "getshedule" {
		group := r.URL.Query().Get("group")
		fullname := r.URL.Query().Get("fullname")
		week, _ := strconv.Atoi(r.URL.Query().Get("week"))
		day := r.URL.Query().Get("day")
		result, _ = json.Marshal(SheduleFor(group, fullname, day, week))
	}
	if command == "sheduletoday" {
		group := r.URL.Query().Get("group")
		fullname := r.URL.Query().Get("fullname")
		result, _ = json.Marshal(SheduleToday(group, fullname))
	}
	if command == "sheduletomorrow" {
		group := r.URL.Query().Get("group")
		fullname := r.URL.Query().Get("fullname")
		result, _ = json.Marshal(SheduleTomorrow(group, fullname))
	}
	if command == "whereteacher" {
		fullname := r.URL.Query().Get("fullname")
		result, _ = json.Marshal(WhereTeacher(fullname))
	}
	if command == "wheregroup" {
		group := r.URL.Query().Get("group")
		result, _ = json.Marshal(WhereGroup(group))
	}
	if command == "addcomment" {
		group := r.URL.Query().Get("group")
		fullname := r.URL.Query().Get("fullname")
		week, _ := strconv.Atoi(r.URL.Query().Get("week"))
		day := r.URL.Query().Get("day")
		number, _ := strconv.Atoi(r.URL.Query().Get("number"))
		text := r.URL.Query().Get("text")
		answer := AddComment(group, fullname, week, day, number, text)
		result, _ = json.Marshal(answer)
	}
	if command == "setshedule" {
		group := r.URL.Query().Get("group")
		week, _ := strconv.Atoi(r.URL.Query().Get("week"))
		day := r.URL.Query().Get("day")
		number, _ := strconv.Atoi(r.URL.Query().Get("number"))
		jsonByte := []byte(r.URL.Query().Get("json"))
		result, _ = json.Marshal(SetShedule(group, week, day, number, jsonByte))
	}
	fmt.Fprint(w, string(result))
}

func NextLesson(group string, fullname string) (LessonData, int) {
	var Shedule [2][7][7]LessonData
	date1 := time.Now()
	date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("MSK", 10800))
	typeOfWeek := int(date1.Sub(date2).Hours()/24/7) % 2
	day := int(time.Now().Weekday() - 1)
	if day == -1 {
		day = 6
	}
	number := int(time.Now().Hour()*60) + int(time.Now().Minute())
	for index, minutes := range sheduleCall {
		if number < minutes {
			number = index - 1
			break
		}
	}
	for number+1 < 7 {
		if fullname == "" {
			file, _ := os.ReadFile("Shedule\\" + group + ".json")
			json.Unmarshal(file, &Shedule)
			if Shedule[typeOfWeek][day][number+1].Type != "" {
				return Shedule[typeOfWeek][day][number+1], number + 1
			}
		} else {
			for _, group := range groups {
				file, _ := os.ReadFile("Shedule\\" + group + ".json")
				json.Unmarshal(file, &Shedule)
				if Shedule[typeOfWeek][day][number+1].Teacher == fullname {
					break
				}
			}
			if Shedule[typeOfWeek][day][number+1].Type != "" {
				return Shedule[typeOfWeek][day][number+1], number + 1
			}
		}
		number = number + 1
	}
	var empty LessonData
	return empty, 0
}

func SheduleFor(group string, fullname string, day string, typeOfWeek int) [7]LessonData {
	var Shedule [2][7][7]LessonData
	if typeOfWeek == -1 {
		date1 := time.Now()
		date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("UTC+3", 3*50*50))
		typeOfWeek = int(date1.Sub(date2).Hours()/24/7) % 2
	}
	if fullname == "" {
		file, _ := os.ReadFile("Shedule\\" + group + ".json")
		json.Unmarshal(file, &Shedule)
		return Shedule[typeOfWeek][weekDays[day]]
	} else {
		var Total [7]LessonData
		for _, group := range groups {
			file, _ := os.ReadFile("Shedule\\" + group + ".json")
			json.Unmarshal(file, &Shedule)
			for index, lesson := range Shedule[typeOfWeek][weekDays[day]] {
				if lesson.Teacher == fullname {
					Total[index] = lesson
				}
			}
		}
		return Total
	}
}

func SheduleToday(group string, fullname string) [7]LessonData {
	var Shedule [2][7][7]LessonData
	date1 := time.Now()
	date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("MSK", 10800))
	typeOfWeek := int(date1.Sub(date2).Hours()/24/7) % 2
	day := int(date1.Weekday() - 1)
	if day == -1 {
		day = 6
	}
	if fullname == "" {
		file, _ := os.ReadFile("Shedule\\" + group + ".json")
		json.Unmarshal(file, &Shedule)
		return Shedule[typeOfWeek][day]
	} else {
		var Total [7]LessonData
		for _, group := range groups {
			file, _ := os.ReadFile("Shedule\\" + group + ".json")
			json.Unmarshal(file, &Shedule)
			for index, lesson := range Shedule[typeOfWeek][day] {
				if lesson.Teacher == fullname {
					Total[index] = lesson
				}
			}
		}
		return Total
	}
}

func SheduleTomorrow(group string, fullname string) [7]LessonData {
	var Shedule [2][7][7]LessonData
	date1 := time.Now().Add(time.Hour * time.Duration(24))
	date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("MSK", 10800))
	typeOfWeek := int(date1.Sub(date2).Hours()/24/7) % 2
	day := int(date1.Weekday() - 1)
	if day == -1 {
		day = 6
	}
	if fullname == "" {
		file, _ := os.ReadFile("Shedule\\" + group + ".json")
		json.Unmarshal(file, &Shedule)
		return Shedule[typeOfWeek][day]
	} else {
		var Total [7]LessonData
		for _, group := range groups {
			file, _ := os.ReadFile("Shedule\\" + group + ".json")
			json.Unmarshal(file, &Shedule)
			for index, lesson := range Shedule[typeOfWeek][day] {
				if lesson.Teacher == fullname {
					Total[index] = lesson
				}
			}
		}
		return Total
	}
}

func WhereGroup(group string) LessonData {
	var Shedule [2][7][7]LessonData
	file, _ := os.ReadFile("Shedule\\" + group + ".json")
	json.Unmarshal(file, &Shedule)
	date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("UTC+3", 3*50*50))
	date1 := time.Now()
	typeOfWeek := int(date1.Sub(date2).Hours()/24/7) % 2
	day := int(time.Now().Weekday() - 1)
	if day == -1 {
		day = 6
	}
	number := int(time.Now().Hour()*60) + int(time.Now().Minute())
	for index, minutes := range sheduleCall {
		if number < minutes {
			number = index
			break
		}
	}
	if number < 7 {
		return Shedule[typeOfWeek][day][number]
	} else {
		var empty LessonData
		return empty
	}
}

func WhereTeacher(fullname string) LessonData {
	var Shedule [2][7][7]LessonData
	date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("UTC+3", 3*50*50))
	date1 := time.Now()
	typeOfWeek := int(date1.Sub(date2).Hours()/24/7) % 2
	day := int(time.Now().Weekday() - 1)
	if day == -1 {
		day = 6
	}
	number := int(time.Now().Hour()*60) + int(time.Now().Minute())
	for index, minutes := range sheduleCall {
		if number < minutes {
			number = index
			break
		}
	}
	for _, group := range groups {
		file, _ := os.ReadFile("Shedule\\" + group + ".json")
		json.Unmarshal(file, &Shedule)
		if Shedule[typeOfWeek][day][number].Teacher == fullname {
			break
		}
	}
	return Shedule[typeOfWeek][day][number]
}

func AddComment(group string, fullname string, week int, dayString string, number int, text string) LessonData {
	var Shedule [2][7][7]LessonData
	var day int
	file, _ := os.ReadFile("Shedule\\" + group + ".json")
	json.Unmarshal(file, &Shedule)
	if week == -1 {
		date1 := time.Now()
		date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("UTC+3", 3*50*50))
		week = int(date1.Sub(date2).Hours()/24/7) % 2
	}
	if dayString == "Сегодня" {
		day = int(time.Now().Weekday() - 1)
		if day == -1 {
			day = 6
		}
	} else {
		if dayString == "Завтра" {
			day = int(time.Now().Add(time.Hour*time.Duration(24)).Weekday() - 1)
			if day == -1 {
				day = 6
			}
		} else {
			day = weekDays[dayString]
		}
	}
	if text == "nul" {
		Shedule[week][day][number-1].Comment = ""
	} else {
		Shedule[week][day][number-1].Comment = fullname + ": " + text
	}
	byteJson, _ := json.Marshal(Shedule)
	os.WriteFile("Shedule\\"+group+".json", byteJson, 0644)
	return Shedule[week][day][number-1]
}

func SetShedule(group string, week int, dayString string, number int, jsonByte []byte) LessonData {
	var Shedule [2][7][7]LessonData
	var NewData LessonData
	var day int
	file, _ := os.ReadFile("Shedule\\" + group + ".json")
	json.Unmarshal(file, &Shedule)
	json.Unmarshal(jsonByte, &NewData)
	if week == -1 {
		date1 := time.Now()
		date2 := time.Date(2023, 9, 4, 12, 0, 0, 0, time.FixedZone("UTC+3", 3*50*50))
		week = int(date1.Sub(date2).Hours()/24/7) % 2
	}
	if dayString == "Сегодня" {
		day = int(time.Now().Weekday() - 1)
		if day == -1 {
			day = 6
		}
	} else {
		if dayString == "Завтра" {
			day = int(time.Now().Add(time.Hour*time.Duration(24)).Weekday() - 1)
			if day == -1 {
				day = 6
			}
		} else {
			day = weekDays[dayString]
		}
	}
	Shedule[week][day][number] = NewData
	byteJson, _ := json.Marshal(Shedule)
	os.WriteFile("Shedule\\"+group+".json", byteJson, 0644)
	return Shedule[week][day][number]
}
