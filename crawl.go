package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"net/http"
	"os"
)

type user struct {
	id         string
	screenName string
}

type result struct {
	user      user
	suspended bool
	deleted   bool
}

const baseUrl string = "https://twitter.com/"
const suspendedUrl string = "https://twitter.com/account/suspended"

// make the HTTP client ignore redirects
var client = &http.Client{
	CheckRedirect: func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse
	},
}

func crashIf(err error) {
	if err != nil {
		log.Fatal(err.Error())
	}
}

// reads a CSV with a tto-do list (expects two columns, no headers, first
// column is user id, second column is user screen name).
func readTodoList(p string) [][]string {
	f, err := os.Open(p)
	crashIf(err)
	defer f.Close()
	log.Println("Reading", p, "…")
	defer log.Println(p, "read!")
	l, err := csv.NewReader(f).ReadAll()
	crashIf(err)
	return l
}

func checkUser(u user) result {
	log.Println("Checking", u.screenName, "…")
	defer log.Println(u.screenName, "checked!")

	r, err := client.Head(baseUrl + u.screenName)
	crashIf(err)
	r.Body.Close() // it's a head request, we have no body any way

	s := false
	if r.StatusCode == 302 {
		for _, location := range r.Header["location"] {
			if location == suspendedUrl {
				s = true
			}
		}
	}
	return result{u, s, r.StatusCode == 404}
}

func main() {
	const workers = 512
	ls := readTodoList("todo.txt")
	queue := make(chan user)
	done := make(chan result)

	// send data to the queue
	for i, s := range ls {
		go func(s []string, i int) {
			queue <- user{s[0], s[1]}
		}(s, i)
	}

	// wire workers to the queue
	for i := 0; i < workers; i++ {
		go func() {
			for u := range queue {
				done <- checkUser(u)
			}
		}()
	}

	f, err := os.Create("status.csv")
	crashIf(err)
	defer f.Close()
	f.WriteString("user,suspended,deleted\n")

	for i := 0; i < len(ls); i++ {
		r := <-done
		f.WriteString(fmt.Sprintf("%s,%t,%t\n", r.user.id, r.suspended, r.deleted))
	}

}
