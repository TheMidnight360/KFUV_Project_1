#define WIN32_LEAN_AND_MEAN
#include <locale.h>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <Windows.h>
#include <WinSock2.h>
#include "include/httplib.h"
#include "include/json.hpp"
#include <urlmon.h>
#pragma comment(lib, "urlmon.lib")
using namespace httplib;
using namespace std;
using json = nlohmann::json;


static void HomeHandler(const Request& req, Response& res) {
	httplib::Client cli("http://localhost:8060");

	auto requestURL = "/login";
	auto& requestHeader = req.headers;
	cli.set_default_headers(requestHeader);
	json js;
	std::string read;
	if (auto response = cli.Get(requestURL)) {
		if (response->status == 200) {
			js = json::parse(response->body);
			std::string line;
			read = response->body;
		}
		else {
			std::cout << "Status error: " << response->status << std::endl;
		}
	}
	else {
		auto err = response.error();
		std::cout << "HTTP error: " << httplib::to_string(err) << std::endl;
	}
	if (js["role"] != "admin") {
		auto html = "Вы не имеете доступа к этому сайту, так как вы не являетесь администратором.";
		res.set_content(html, "text/plain");
		return;
	}
	auto html = "<!DOCTYPE html>\
		<html>\
		<head>\
		<title>Расписание КФУ: администратор</title>\
		</head>\
		<body>\
		\
		<button type=\"button\">Обновить расписание</button>\
		<h1>This is a Heading</h1>\
		<p>This is a paragraph.</p>\
		\
		</body>\
		</html>";
	string URL = "https://schedule-cloud.cfuv.ru/index.php/s/YLoTDF3GqDjnDbR/download/09.03.01%20%D0%98%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0%20%D0%B8%20%D0%B2%D1%8B%D1%87%D0%B8%D1%81%D0%BB%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F%20%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0,09.03.04%20%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BD%D0%B0%D1%8F%20%D0%B8%D0%BD%D0%B6%D0%B5%D0%BD%D0%B5%D1%80%D0%B8%D1%8F%20%281-4%29.xlsx";
	string FilePath = "C:\\Users\\themi\\OneDrive\\Downloads\\file.xlsx";

	LPCSTR wideStringUrl = URL.c_str();
	LPCSTR wideStringPath = FilePath.c_str();
	auto result = URLDownloadToFileA(0, wideStringUrl, wideStringPath, BINDF_GETNEWESTVERSION, 0);
	cout << "SUCCEEDED: " << (SUCCEEDED(result)) << endl;
	res.set_content(html, "html");
}

int main() {
	Server svr;
	svr.Get("/", HomeHandler);
	svr.listen("0.0.0.0", 8040);
}