from datetime import datetime, date, timedelta
from abc import abstractmethod, ABC
import pickle
from collections import UserDict
from functools import wraps

class Field(ABC):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    @abstractmethod
    def value(self, value):
        self.value=self.value

class Name(Field):
    def __init__(self,value):
        if len(value) !=0:
            super().__init__(value)
        else:
            raise ValueError ("Name cannot be empty")

    def value(self, value):
        return self.value
		
class Phone(Field):
    def __init__(self, value:str) -> None :
        if len(value)==10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Phone number must be 10 digits like:0671234567")

    def value(self, value):
        return super().value(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            if self.__is_valid(value):
                self.value = value
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __is_valid(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def value(self, value):
        return super().value(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __find(self, phone: str,get_instance: bool = False) -> int | Phone | None:
        #якщо пошук з двома аргументами - повертає значення, інакше позицію входження
        for id, instance in enumerate(self.phones):
            if instance.value == phone:
                return instance if get_instance else id
        return None

    def add_phone(self, phone : str):

        if self.__find(phone,True):
             # If already exists - do nothing
             pass
        else:
            self.phones.append(Phone(phone))

    def find_phone(self, phone : str):
        return self.__find(phone, True)

    def remove_phone (self, phone :str):
        if (id := self.__find(phone)) is not None:
            del self.phones[id]

    def edit_phone(self, old: str, new : str):
        if (id := self.__find(old)) is None:
            raise ValueError(f'Phone {old} not found!')
        else:
            self.phones[id] = Phone(new)

    def add_birthday(self, bday:str):
        if not self.birthday:
            self.birthday = Birthday(bday)

    def __str__(self):
        return f"Contact name: {self.name.value}, Birthday: {self.birthday}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record:Record) -> Record | None:
        self.data[record.name.value]=record
    
    def find(self, name: str) -> Record:
        return self.data.get(name)
    
    def delete(self, name) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Запис {name} не знайдено")

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []
        for name, record in self.data.items():
            if not record.birthday is None:
                
                bday_this_year = datetime.strptime(record.birthday.value,"%d.%m.%Y").replace(year=today.year).date()
                if bday_this_year<today:
                    bday_this_year = datetime.strptime(record.birthday.value,"%d.%m.%Y").replace(year=today.year+1).date()
                next_week = today + timedelta(days = 7)
                if bday_this_year.weekday() >= 5:
                    bday_this_year = bday_this_year + timedelta(7-bday_this_year.weekday())
                    
                if today <= bday_this_year <= next_week:
                   upcoming.append({"name": name, "birthday_date": bday_this_year.strftime("%d.%m.%Y")})
                
            
        return upcoming
     
    def __str__(self) ->str:
        result=''
        for name, record in self.data.items():
            result+=str(record)+'\n'
        return result.strip()

class UserInterface(ABC):

    @abstractmethod
    def dispay_book(self,book):
        pass

    @abstractmethod
    def display_cmds(self):
        pass

class CLInterface(UserInterface):

    def dispay_book(self, book):
        print(book)

    def display_cmds(self):
        return list(HANDLERS.keys())

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
def hello(args,book):
    return "How can I help you?"

def exit(args, book):
    return book

def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            if func.__name__ == "add_contact":
                return ValueError("Invalid input. Use 'add [name] [10 digits phone]'")
            elif func.__name__ == "change_contact":
                return ValueError("Invalid input. Use 'change [name] [old_phone] [new_phone]'")
            elif func.__name__ == "get_phone":
                return ValueError("Invalid input. Use 'phone [name]'")
            elif func.__name__ == "add_birthday":
                return ValueError("Invalid input. Use 'add-birthday [name] [date of birth in DD.MM.YYYY format]'")
            elif func.__name__ == "show_birthday":
                return ValueError("Invalid input. Use 'show-birthday [name]'")
            else:
                return ValueError("Invalid command")
            
        


    return wrapper

@input_error
def add_contact(args, book):
    if len(args)< 2:
        raise ValueError("Please type add name phone")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) != 3 or not Phone(args[1]).value or not Phone(args[2]).value:
        raise ValueError("Invalid input. Use 'change [name] [old_phone] [new_phone]'")
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
    return "Contact updated"

@input_error
def get_phone(args,book):

    name, *_ = args
    record=book.find(name)
    if record:
        user_phones=[]
        for phone in record.phones:
           user_phones.append(phone.value)
        return f"{name}'s phone numbers: {"; ".join(user_phones)}"
    else:
        return "Not Found"


def get_all(args,book):
    return book

@input_error
def add_birthday(args, book):
    name, bday,*_ = args
    if record := book.find(name):
        if record.birthday is None:
            record.add_birthday(bday)
            return f"Birthday at {record.birthday} added for {name}"
    else:
        return f"Contact {name} not found"

@input_error
def show_birthday(args, book):
    name, *_ = args
    if record := book.find(name):
        if not record.birthday is None:
            return f"{name}'s birthday is at {record.birthday}"
        else:
            return f"No birthday specified for {name}"
    else:
        return f"Contact {name} not found"

def birthdays(args, book):
    return book.get_upcoming_birthdays()

HANDLERS = {
    'add' : add_contact,
    'hello': hello,
    'change' :change_contact,
    'phone' : get_phone,
    'all' : get_all,
    'add-birthday' : add_birthday,
    'show-birthday' : show_birthday,
    'birthdays' : birthdays,
    'exit' : exit,
    'close' : exit

}

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = load_data()
    ui=CLInterface()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if len(user_input.strip())==0:
            print(f"No command entered: try {ui.display_cmds()}")
            continue
        else:
            command, *args = parse_input(user_input)

        if command in HANDLERS.keys():
            if command in ['close', 'exit']:
                ui.dispay_book(book)
                save_data(book)
                print("Goodbye!")
                break
                           
            print (HANDLERS.get(command)(args, book))

        

        else:
            print(f"Invalid command.try {ui.display_cmds()}")
        

if __name__ == "__main__":
    main()