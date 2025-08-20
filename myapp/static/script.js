document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("form3Example1c").value;
    const email = document.getElementById("form3Example3c").value;
    const password = document.getElementById("form3Example4c").value;

    // Формируем объект для FastAPI
    const payload = {
        name: name,
        email: email,
        password: password,
        extra_info: {
            city: null
        }
    };

    try {
        const response = await fetch("http://localhost:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert("Регистрация прошла успешно!");
            console.log(data);  // зарегистрированный пользователь
        } else {
            alert("Ошибка: " + data.detail);
        }
    } catch (error) {
        console.error("Ошибка при запросе:", error);
    }
});

