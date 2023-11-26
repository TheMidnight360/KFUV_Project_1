package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type GitData struct {
	Id   int64  `json:"id"`
	Name string `json:"name"`
}

type UserData struct {
	Github_id      int64  `json:"github_id"`
	Telegram_id    int64  `json:"telegram_id"`
	Name           string `json:"name"`
	Surname        string `json:"surname"`
	Patronymic     string `json:"patronymic"`
	Role           string `json:"role"`
	Group          string `json:"group"`
	Recent_command string `json:"recent_command"`
}

var token string
var SECRET = "3685"

var authenticate struct {
	is_done bool
	code    string
}

const (
	CLIENT_ID     = "43372e1074ad744a80f1"
	CLIENT_SECRET = "db973eaeb113251c1d9a4624e733860f5ee9dc34"
)

func main() {
	http.HandleFunc("/register", RegisterHandler)
	http.HandleFunc("/oauth", OauthHandler)
	http.HandleFunc("/login", LoginHandler)
	http.HandleFunc("/setuser", SetUserHandler)
	http.ListenAndServe(":8060", nil)
}

func CookieJWT(r *http.Request) UserData {
	var data UserData
	cookie, err := r.Cookie("JWT")
	if err == http.ErrNoCookie {
		data.Name = "none"
		return data
	}
	token, _ := jwt.Parse(cookie.Value, func(token *jwt.Token) (interface{}, error) {
		return []byte(SECRET), nil
	})
	payload, ok := token.Claims.(jwt.MapClaims)
	if ok && token.Valid {
		data.Github_id = int64(payload["github_id"].(float64))
		data.Name = payload["name"].(string)
	}
	return data
}

func CookieTelegram(r *http.Request) int64 {
	cookie, err := r.Cookie("Telegram_id")
	if err == http.ErrNoCookie {
		return 0
	}
	telegram_id, _ := strconv.ParseInt(cookie.Value, 10, 64)
	return telegram_id
}

func FindUser(array []UserData, telegram int64, github int64) (UserData, int) {
	for index, user := range array {
		if user.Github_id == github || user.Telegram_id == telegram {
			return user, index
		}
	}
	var empty UserData
	return empty, -1
}

func UpdateUser(array *[]UserData, request UserData, index int) UserData {
	temp := *array
	if request.Telegram_id != 0 && request.Github_id != 0 {
		telegram, telegramInd := FindUser(*array, request.Telegram_id, 0)
		github, githubInd := FindUser(*array, 0, request.Github_id)
		if telegramInd == -1 && githubInd != -1 {
			temp[index].Telegram_id = request.Telegram_id
		} else {
			if telegramInd != -1 && githubInd == -1 {
				temp[index].Github_id = request.Github_id
			} else {
				if github.Telegram_id != request.Telegram_id || telegram.Github_id != request.Github_id {
					DeleteUser(&temp, github)
					index = telegramInd
					temp[index].Github_id = request.Github_id
				}
			}
		}
	}
	if request.Name != "" {
		temp[index].Name = request.Name
	}
	if request.Surname != "" {
		temp[index].Surname = request.Surname
	}
	if request.Patronymic != "" {
		temp[index].Patronymic = request.Patronymic
	}
	if request.Group != "" {
		temp[index].Group = request.Group
	}
	if request.Role != "" {
		temp[index].Role = request.Role
	}
	if request.Recent_command != "" {
		temp[index].Recent_command = request.Recent_command
	}
	*array = temp
	return temp[index]
}

func DeleteUser(array *[]UserData, request UserData) {
	temp := *array
	var ind = 0
	for ind != -1 {
		_, ind = FindUser(temp, request.Telegram_id, request.Github_id)
		if ind != -1 {
			temp[ind] = temp[len(temp)-1]
			temp = temp[:len(temp)-1]
		}
	}
	*array = temp
}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	var userFind UserData
	var telegram_id int64
	var github_id int64
	var UsersData []UserData
	var result string
	var user UserData = CookieJWT(r)
	byteJson, _ := os.ReadFile("UsersData.json")
	json.Unmarshal(byteJson, &UsersData)
	if user.Github_id <= 0 {
		telegram_id, _ = strconv.ParseInt(r.URL.Query().Get("telegram_id"), 10, 64)
		github_id, _ = strconv.ParseInt(r.URL.Query().Get("github_id"), 10, 64)
		userFind, _ = FindUser(UsersData, telegram_id, github_id)
	} else {
		userFind, _ = FindUser(UsersData, 0, user.Github_id)
	}
	if userFind.Github_id <= 0 {
		user.Recent_command = "UNAUTHORIZED"
	} else {
		user = userFind
	}
	byteJson, _ = json.Marshal(user)
	result = string(byteJson[:])
	authenticate.is_done = false
	fmt.Fprint(w, result)
}

func RegisterHandler(w http.ResponseWriter, r *http.Request) {
	telegram_id, _ := strconv.ParseInt(r.URL.Query().Get("telegram_id"), 10, 64)
	cookies := http.Cookie{
		Name:     "Telegram_id",
		Value:    strconv.FormatInt(telegram_id, 10),
		Path:     "/",
		MaxAge:   3600,
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
	}
	http.SetCookie(w, &cookies)
	link := "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID
	http.Redirect(w, r, link, http.StatusSeeOther)
}

func SetUserHandler(w http.ResponseWriter, r *http.Request) {
	var request UserData
	var github_admin int64
	request.Telegram_id, _ = strconv.ParseInt(r.URL.Query().Get("telegram_id"), 10, 64)
	request.Github_id, _ = strconv.ParseInt(r.URL.Query().Get("github_id"), 10, 64)
	request.Surname = r.URL.Query().Get("surname")
	request.Name = r.URL.Query().Get("name")
	request.Patronymic = r.URL.Query().Get("patronymic")
	request.Group = r.URL.Query().Get("group")
	request.Role = r.URL.Query().Get("role")
	request.Recent_command = r.URL.Query().Get("recent_command")
	github_admin, _ = strconv.ParseInt(r.URL.Query().Get("github_admin"), 10, 64)
	byteJson, _ := os.ReadFile("UsersData.json")
	var UsersData []UserData
	json.Unmarshal(byteJson, &UsersData)
	admin, _ := FindUser(UsersData, 0, github_admin)
	if admin.Role == "admin" && request.Role != "" {
		if request.Role == "admin" && request.Github_id != admin.Github_id {
			request.Role = ""
		}
	} else {
		request.Role = ""
	}
	_, ind := FindUser(UsersData, request.Telegram_id, request.Github_id)
	if ind != -1 {
		newUser := UpdateUser(&UsersData, request, ind)
		byteJson, _ = json.Marshal(UsersData)
		os.WriteFile("UsersData.json", byteJson, 0644)
		byteJson, _ = json.Marshal(newUser)
		result := string(byteJson[:])
		fmt.Fprint(w, result)
		return
	}
	if request.Role == "" {
		request.Role = "student"
	}
	UsersData = append(UsersData, request)
	byteJson, _ = json.Marshal(UsersData)
	os.WriteFile("UsersData.json", byteJson, 0644)
	byteJson, _ = json.Marshal(request)
	result := string(byteJson[:])
	fmt.Fprint(w, result)
}

func OauthHandler(w http.ResponseWriter, r *http.Request) {
	var user UserData
	var answer string
	var UsersData []UserData
	byteJson, _ := os.ReadFile("UsersData.json")
	json.Unmarshal(byteJson, &UsersData)
	telegram_id := CookieTelegram(r)
	code := r.URL.Query().Get("code")
	data := getUserData(getAccessToken(code))
	if code != "" {
		user.Github_id = data.Github_id
		user.Telegram_id = telegram_id
		user.Name = data.Name
		authenticate.is_done = true
		authenticate.code = code
		cookies := http.Cookie{
			Name:     "JWT",
			Value:    token,
			Path:     "/",
			MaxAge:   3600,
			HttpOnly: true,
			Secure:   true,
			SameSite: http.SameSiteLaxMode,
		}
		http.SetCookie(w, &cookies)
		client := http.Client{}
		requestURL := fmt.Sprintf("http://localhost:8060/setuser?telegram_id=%d&github_id=%d&name=%s", user.Telegram_id, user.Github_id, user.Name)
		request, _ := http.NewRequest("GET", requestURL, nil)
		client.Do(request)
		if telegram_id != 0 {
			answer = "Аккаунт Github успешно сохранен и привязан к вашему аккаунту Telegram. Вы можете закрыть данную страницу."
		} else {
			answer = "Аккаунт Github успешно сохранен. Вы можете закрыть данную страницу."
		}
	} else {
		answer = "Произошла неизвестная ошибка. Попробуйте еще раз."
	}
	fmt.Fprint(w, answer)
}

func getAccessToken(code string) string {
	client := http.Client{}
	requestURL := "https://github.com/login/oauth/access_token"

	form := url.Values{}
	form.Add("client_id", CLIENT_ID)
	form.Add("client_secret", CLIENT_SECRET)
	form.Add("code", code)

	request, _ := http.NewRequest("POST", requestURL, strings.NewReader(form.Encode()))
	request.Header.Set("Accept", "application/json")
	response, err := client.Do(request)
	if err != nil {
		return ""
	}
	defer response.Body.Close()

	var responsejson struct {
		AccessToken string `json:"access_token"`
	}
	json.NewDecoder(response.Body).Decode(&responsejson)
	return responsejson.AccessToken
}

func getUserData(AccessToken string) UserData {
	client := http.Client{}
	requestURL := "https://api.github.com/user"
	request, _ := http.NewRequest("GET", requestURL, nil)
	request.Header.Set("Authorization", "Bearer "+AccessToken)
	response, err := client.Do(request)
	var data GitData
	var user UserData
	if err != nil {
		return user
	}
	defer response.Body.Close()
	tokenExpiresAt := time.Now().Add(time.Hour * time.Duration(24))
	json.NewDecoder(response.Body).Decode(&data)
	payload := jwt.MapClaims{
		"github_id":  data.Id,
		"name":       data.Name,
		"expires_at": tokenExpiresAt.Unix(),
	}
	user.Name = data.Name
	user.Github_id = data.Id
	tokenJwt := jwt.NewWithClaims(jwt.SigningMethodHS256, payload)
	tokenString, _ := tokenJwt.SignedString([]byte(SECRET))
	token = tokenString
	return user
}
