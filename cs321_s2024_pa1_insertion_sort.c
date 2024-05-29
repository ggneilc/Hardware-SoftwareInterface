/* To compile this program:
 *   gcc cs321_s2024_pa1_insertion_sort.c -o cs321_s2024_pa1_insertion_sort
 * Change N and recompile to run on arrays of different sizes.
 *
 * For this assignment, you'll be implementing insertion sort in the LEG
 * subset of the ARMv8 ISA.  Insertion sort is an n-squared comparison sort
 * which you should all be familiar with from your data structures
 * course.
 *
 * Regardless of how comfortable you may be with insertion sort, or with how
 * well you may comprehend this C implementation, we want to stress here that
 * you do not have to understand this algorithm!  You don't even have to try
 * to understand it.  All that you have to do is, essentially, be the
 * compiler and translate this C code into LEGv8.  This is not to discourage
 * understanding.  Understanding is a good and useful thing.  We are simply
 * pointing out that you don't need to understand the algorithm in order to
 * implement your solution.  It's not rare that a route of expedience is
 * optimal.
 *
 * See the comments and code below for details on exactly what you must 
 * implement.
 */

#define N 512

/* Here is a single-function version of insertion sort.  This, or something
 * very similar, is probably what you would write if you were doing this in a
 * higher-level language.
 *
 * Below, we break this into a number of smaller functions.  We do this for
 * two reasons:
 *
 *   1) The bigger a procedure is, the more difficult it (usually) is to 
 *      implement it in assembly (in particular, the refactor eliminates
 *      nested loops); and
 *   2) We want to force you to implement multiple procedures, use the stack,
 *      and adhere to ARMv8 calling conventions.
 *
 * You will NOT be implementing this function.  You'll be implementing the
 * broken-down version of it below.  This version is only here for reference.
 */
void insertion_sort_one_function_do_not_implement(long long *a,
                                                  long long n)
{
  long long i, j, t;
  
  for (i = 1; i < n; i++) {
    for (t = a[i], j = i - 1; j > -1 && a[j] > t; j--) {
      a[j + 1] = a[j];
    }
    a[j + 1] = t;
  }
}

/* Copies the value what into array a at index where */
void is_insert(long long *a, long long what, long long where)
{
  a[where] = what;
}

/* Given array a and index end where the items in a at indices less *
 * than end are in non-decreasing order, overwrites the item at     *
 * index end and shifts all elements larger than the element        *
 * originally at a[end] one position toward the end of the array,  *
 * thus creating a hole for the original a[end] in its sorted      *
 * position.  Returns the index of the hole.                        */
long long is_shift(long long *a, long long end)
{
  long long i, tmp;
  
  for (tmp = a[end], i = end - 1; i > -1 && a[i] > tmp; i--) {
    a[i + 1] = a[i];
  }

  return i + 1;
}

/* Sorts array a containing n elements into non-descending order. */
void insertion_sort(long long *a, long long n)
{
  long long i, value;

  for (i = 1; i < n; i++) {
    value = a[i];
    is_insert(a, value, is_shift(a, i));
  }
}

/* fill fills the array a (of n elements) with decreasing values from *
 * n - 1 to zero (reverse sorted order).                              */
void fill(long long *a, long long n) {
  long long i;
  
  for (i = 0; i < n; i++) {
    a[i] = n - i - 1;
  }
}

/* This is a standard, iterative binary search.  a is the base address *
 * of your array.  start is the base index of the search space in a.   *
 * end is the final index of the search space in a.  value is the      *
 * value that is being sought.  a must be in sorted order.  Returns    *
 * the index of the first element found wherein the value of the       *
 * element is value.  Returns -1 if value is not found in a.           */
long log binary_search(long long *a, long long start,
		       long long end, long long value)
{
  long long m;

  while (start <= end) {
    m = (((end + start) + 1) / 2);

    if (a[m] == value) {
      return m;
    }

    if (value > a[m]) {
      start = m + 1;
    } else {
      end = m - 1;
    }
  }
  
  return -1;
}

/* Your main function should allocate space for an array, call fill to   *
 * fill it with decreasing numbers, and then call insertion_sort to sort *
 * it.  Use the HALT emulator instruction to see the memory contents and *
 * confirm that your functions work.  You may choose any array size you  *
 * like (up to the default limit of memory, 4096 bytes or 512 8-byte     *
 * integers).                                                            *
 *                                                                       * 
 * After sorting, call binary search with 4 values: the smallest,        *
 * largest, and middle items in your array, followed by a value not in   *
 * the array.  After each call PRNT X0 to display the return value.      *
 *                                                                       *
 * After completing all of the above, HALT the emulator to force a core  *
 * dump so that you (and the TAs) can examine the contents of memory.    *
 *                                                                       *
 * You must implement all functions described above except for the       *
 * reference implementation of insertion sort.  You are acting as the    *
 * compiler here; you are not granted creative freedom to refactor these *
 * functions to your liking.  You must adhere to ARMv8 calling           *
 * conventions; in particular, you must correctly use the stack when     *
 * calling and implementing procedures, and a procedure may not "know"   *
 * anything that it was not explicitly informed of by way of its         *
 * parameters!  For example: Even though you--the programmer--know that  *
 * no other procedure uses X22, you still must save it before you use it *
 * and restore it when you are finished with it.  Imagine that, instead  *
 * of you writing all of these procedures, each of them is written by a  *
 * different person, but none of you are permitted to communicate with   *
 * each other in any way.  The only thing each of you has is this        *
 * specification.  When we put all of your procedures together, your     *
 * program should work, but the only way that will be possible is if you *
 * fully adhere to convention.                                           *
 *                                                                       *
 * You may work alone or with up to 1 partner on this assignment.        */
int main(int argc, char *argv[])
{
  /* In your LEGv8 program, main will not be a procedure.  Control will *
   * begin at the top of the file, so you should think of that as main. *
   * If control reaches the end of the file, the program will exit,     *
   * which you may think of as leaving main.                            */

  long long a[N];

  fill(a, N);

  insertion_sort(a, N);

  /* Returns 0 */
  binary_search(a, 0, N - 1, 0);
  /* Returns 511 (N - 1) */
  binary_search(a, 0, N - 1, N - 1);
  /* Returns 255 ((N - 1) / 2) */
  binary_search(a, 0, N - 1, N / 2);
  /* Returns -1 */
  binary_search(a, 0, N - 1, N);
  
  return 0;
}
