# Database Normalization

## 1. Introduction: Why Do We Need "Good" Database Design?

So far, we've learned how to create tables and store data. But how do we know if our table structure is "good"? A poorly designed database can lead to significant problems that are difficult to fix later.

Consider a single, large table to store all information about student enrollments:

**`Student_Enrollments`**
| StudentID | StudentName | StudentEmail | CourseID | CourseTitle | InstructorName | InstructorOffice |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 101 | Alice | alice@uni.edu | CS101 | Intro to CS | Dr. Smith | Room 301 |
| 102 | Bob | bob@uni.edu | CS101 | Intro to CS | Dr. Smith | Room 301 |
| 101 | Alice | alice@uni.edu | MTH202 | Calculus II | Dr. Jones | Room 405 |

This design seems simple, but it's full of traps:

*   **Data Redundancy:** Information is repeated unnecessarily. Alice's name and email are stored for every class she takes. Dr. Smith's name and office are stored for every student in his class. This wastes space.

*   **Update Anomaly:** If Dr. Smith moves to a new office, we must find and update **every single row** where he is the instructor. If we miss even one, the data becomes inconsistent.

*   **Insertion Anomaly:** How can we add a new student who hasn't enrolled in any courses yet? We can't, because a `CourseID` is required. Similarly, how do we add a new course that has no students enrolled yet?

*   **Deletion Anomaly:** If Alice drops her only course (MTH202), and we delete that row, we might lose all information about her (her name and email) if she's not in any other courses.

**Database Normalization** is the formal process for analyzing and correcting these problems. It's a systematic technique for decomposing tables to eliminate data redundancy and undesirable anomalies. The foundation of normalization is **functional dependency**.

---

## 2. Functional Dependencies (FDs)

A **functional dependency** is a constraint between two sets of attributes in a relation (table). It describes how the value of one attribute (or a set of attributes) determines the value of another attribute.

We write a functional dependency as:

`X -> Y`

This is read as "**X functionally determines Y**" or "**Y is functionally dependent on X**".

It means that for any two rows in the table, if the values of the attributes in `X` are the same, then the values of the attributes in `Y` must also be the same.

*   `X` is called the **determinant**.
*   `Y` is called the **dependent**.

### Examples

Let's use our `Student_Enrollments` table:

1.  `StudentID -> StudentName`
    *   **Meaning:** If you know the `StudentID`, you know the `StudentName`. For any given `StudentID` (e.g., 101), the `StudentName` will always be the same ("Alice").

2.  `CourseID -> CourseTitle`
    *   **Meaning:** If you know the `CourseID` (e.g., "CS101"), you know the `CourseTitle` ("Intro to CS").

3.  `{StudentID, CourseID} -> InstructorName`
    *   **Meaning:** If you know both the `StudentID` and the `CourseID`, you can determine the instructor for that specific enrollment. This is a **composite determinant**.

4.  `StudentName -> StudentID`
    *   Is this a valid FD? Not necessarily. Two different students could have the same name (e.g., two "John Smith"s). Therefore, `StudentName` does not uniquely determine `StudentID`.

### Keys and Functional Dependencies

Functional dependencies are the formal way to define keys:

*   **Superkey:** A set of attributes `X` is a superkey for a table if `X` functionally determines all other attributes in the table.
    *   Example: `{StudentID, CourseID}` is a superkey for our `Student_Enrollments` table.

*   **Candidate Key:** A **minimal** superkey. No attribute can be removed from the key without it losing its uniqueness.
    *   Example: `{StudentID, CourseID}` is a candidate key. If we remove `StudentID`, `CourseID` alone doesn't determine the student. If we remove `CourseID`, `StudentID` alone doesn't determine the course enrollment details.

*   **Primary Key:** The candidate key chosen by the database designer to be the main identifier for the table.

*   **Prime Attribute:** An attribute that is part of *any* candidate key.
*   **Non-Prime Attribute:** An attribute that is *not* part of any candidate key.

---

## 3. The Normal Forms

Normalization is a step-by-step process. Each step corresponds to a "normal form." We'll focus on the first three, which are the most critical for practical database design.

### First Normal Form (1NF)

**Rule:** A table is in 1NF if:
1.  All attribute values are **atomic** (indivisible).
2.  There are no **repeating groups**.

This is the most basic requirement for any relational database table.

**Bad Design (Not in 1NF):**
| StudentID | Name | PhoneNumbers |
| :--- | :--- | :--- |
| 101 | Alice | "555-1234, 555-5678" |
| 102 | Bob | "555-8888" |

The `PhoneNumbers` column is not atomic; it contains multiple values.

**Fix (Achieving 1NF):** Decompose into two tables.

**`Students`**
| StudentID (PK) | Name |
| :--- | :--- |
| 101 | Alice |
| 102 | Bob |

**`Student_Phones`**
| StudentID (FK) | PhoneNumber |
| :--- | :--- |
| 101 | 555-1234 |
| 101 | 555-5678 |
| 102 | 555-8888 |

Now, every cell holds a single, atomic value.

### Second Normal Form (2NF)

**Prerequisite:** The table must be in 1NF.

**Rule:** No non-prime attribute is **partially dependent** on any candidate key.

In simpler terms: All non-key attributes must depend on the **entire** primary key, not just a part of it. This rule only applies to tables with composite primary keys.

**Bad Design (In 1NF, but not 2NF):**
Let's look at a simplified version of our original table.

**`Enrollments`** (Primary Key: `{StudentID, CourseID}`)
| StudentID | CourseID | StudentName | CourseTitle |
| :--- | :--- | :--- | :--- |
| 101 | CS101 | Alice | Intro to CS |
| 102 | CS101 | Bob | Intro to CS |

**Functional Dependencies:**
*   `StudentID -> StudentName` (This is a **partial dependency** because `StudentName` depends only on `StudentID`, which is just *part* of the primary key).
*   `CourseID -> CourseTitle` (This is also a **partial dependency**).

**Fix (Achieving 2NF):** Decompose the table to remove the partial dependencies.

**`Students`**
| StudentID (PK) | StudentName |
| :--- | :--- |
| 101 | Alice |
| 102 | Bob |

**`Courses`**
| CourseID (PK) | CourseTitle |
| :--- | :--- |
| CS101 | Intro to CS |

**`Enrollment_Junction`**
| StudentID (FK) | CourseID (FK) |
| :--- | :--- |
| 101 | CS101 |
| 102 | CS101 |

Now, there are no partial dependencies. The junction table only contains the primary key attributes.

### Third Normal Form (3NF)

**Prerequisite:** The table must be in 2NF.

**Rule:** No non-prime attribute is **transitively dependent** on the primary key.

In simpler terms: No non-key attribute should depend on another non-key attribute.

**Bad Design (In 2NF, but not 3NF):**

**`Courses_Info`** (Primary Key: `CourseID`)
| CourseID | CourseTitle | InstructorID | InstructorName |
| :--- | :--- | :--- | :--- |
| CS101 | Intro to CS | I-50 | Dr. Smith |
| MTH202 | Calculus II | I-60 | Dr. Jones |

**Functional Dependencies:**
*   `CourseID -> InstructorID` (Good, depends on the key)
*   `InstructorID -> InstructorName` (This is a **transitive dependency**. `InstructorName` depends on `InstructorID`, which is a non-key attribute, which in turn depends on the primary key `CourseID`).

The chain is: `CourseID -> InstructorID -> InstructorName`.

**Fix (Achieving 3NF):** Decompose to remove the transitive dependency.

**`Courses`**
| CourseID (PK) | CourseTitle | InstructorID (FK) |
| :--- | :--- | :--- |
| CS101 | Intro to CS | I-50 |
| MTH202 | Calculus II | I-60 |

**`Instructors`**
| InstructorID (PK) | InstructorName |
| :--- | :--- |
| I-50 | Dr. Smith |
| I-60 | Dr. Jones |

Now, `InstructorName` is in its own table where it depends directly on its primary key, `InstructorID`.

---

## 4. Conclusion

By applying the principles of normalization, we can transform a large, problematic table into a set of smaller, well-structured tables.

**Our final, normalized design for the original problem:**

1.  **`Students` Table (3NF)**
    *   `StudentID` (PK), `StudentName`, `StudentEmail`

2.  **`Instructors` Table (3NF)**
    *   `InstructorID` (PK), `InstructorName`, `InstructorOffice`

3.  **`Courses` Table (3NF)**
    *   `CourseID` (PK), `CourseTitle`, `InstructorID` (FK)

4.  **`Enrollments` Table (3NF)**
    *   `StudentID` (FK), `CourseID` (FK)
    *   (Primary Key is `{StudentID, CourseID}`)

This design eliminates all the anomalies we identified:
*   **No Redundancy:** Each piece of information is stored only once.
*   **Updates are Easy:** Change an instructor's office in one place in the `Instructors` table.
*   **Insertions are Possible:** You can add a new student to the `Students` table without enrolling them in a course.
*   **Deletions are Safe:** Deleting an enrollment from the `Enrollments` table does not delete the student or the course itself.

Normalization up to 3NF is a fundamental skill for any database designer and is sufficient for the vast majority of application databases.