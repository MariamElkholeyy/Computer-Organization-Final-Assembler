# Commonly used Functions
def hex_to_binary(hex_code):
    hex_to_binary_dict = {
        '0': '0000',
        '1': '0001',
        '2': '0010',
        '3': '0011',
        '4': '0100',
        '5': '0101',
        '6': '0110',
        '7': '0111',
        '8': '1000',
        '9': '1001',
        'A': '1010',
        'B': '1011',
        'C': '1100',
        'D': '1101',
        'E': '1110', 
        'F': '1111'
    }

    binary_code = ""
    for hex_digit in hex_code.upper():
        if hex_digit not in hex_to_binary_dict:
            raise ValueError(f"Invalid hexadecimal character: {hex_digit}")
        binary_code += hex_to_binary_dict[hex_digit]

    return binary_code

def get_binary_code(instruction, addressing_mode):
    hex_code = MR_instruction_map[instruction][addressing_mode] 
    return hex_to_binary(hex_code)

def decimal_to_binary(decimal_number):
    if decimal_number == 0:
        return "0"
    
    is_negative = decimal_number < 0
    decimal_number = abs(decimal_number)
    
    binary_number = ""
    
    while decimal_number > 0:
        binary_number = str(decimal_number % 2) + binary_number
        decimal_number //= 2
    
    if is_negative:
        num_bits = len(binary_number)
        max_binary = '1' * num_bits
        two_complement = int(max_binary, 2) + 1
        binary_number = bin(two_complement)[2:]
    
    return binary_number

def twos_complement_xor(binary_str):
    mask = (1 << len(binary_str)) - 1
    inverted = int(binary_str, 2) ^ mask
    return bin(inverted + 1)[2:].zfill(len(binary_str))

#MAPS 

MR_instruction_map = {
    "AND": ["0", "8"],
    "ADD": ["1", "9"],
    "LDA": ["2", "A"],
    "STA": ["3", "B"],
    "BUN": ["4", "C"],
    "BSA": ["5", "D"],
    "ISZ": ["6", "E"], 
}

In_Out_instruction_map = {
    "INP" : 1111100000000000 ,
    "OUT" : 1111010000000000 , 
    "SKI" : 1111001000000000,
    "SKO" : 1111000100000000,
    "ION" : 1111000010000000 ,
    "IOF" : 1111000001000000
}

Register_instruction_map = {
    'CLA': 7800,
    'CLE': 7400,
    'CMA': 7200,
    'CME': 7100,
    'CIR': 7080,
    'CIL': 7040,
    'INC': 7020,
    'SPA': 7010,
    'SNA': 7008,
    'SZA': 7004,
    'SZE': 7002,
    'HLT': 7001
}


#First Pass

def first_pass_assembler_sl(assembly_code):
    symbol_table = {}
    symbol_labels = {}
    location_counter = 0

    for line in assembly_code.split('\n'):
        tokens = line.split()

        if tokens and tokens[0] not in ["ORG", "END"]:
            if tokens[0].endswith(","):
                symbol_table[tokens[0].strip(",")] = location_counter
            else:
                symbol_table[tokens[0]] = location_counter

        if tokens and len(tokens) >= 2 and tokens[0] == "ORG":
            location_counter = int(tokens[1])

        if len(tokens) >=2 and tokens[0].endswith(","):
            symbol_labels[tokens[0].strip(',')] = location_counter
            
        if tokens and tokens[0] not in ["ORG", "END", ";"]:
            location_counter += 1

    return symbol_labels

def first_pass_assembler_st(assembly_code):
    symbol_table = {}
    symbol_labels = {}
    location_counter = 0

    for line in assembly_code.split('\n'):
        tokens = line.split()

        if tokens and tokens[0] not in ["ORG", "END"]:
            if tokens[0].endswith(","):
                symbol_table[tokens[0].strip(",")] = location_counter
            else:
                symbol_table[tokens[0]] = location_counter

        if tokens and len(tokens) >= 2 and tokens[0] == "ORG":
            location_counter = int(tokens[1])

        if len(tokens) >=2 and tokens[0].endswith(","):
            symbol_labels[tokens[0].strip(',')] = location_counter
            
        if tokens and tokens[0] not in ["ORG", "END", ";"]:
            location_counter += 1

    return symbol_table



#Second Pass 
          
def second_pass_assembler(assembly_code):
    symbol_table = first_pass_assembler_st(assembly_code)
    location =[]
    opcode = None
    address = None
    instruction = []
    for  line in assembly_code.split('\n'):
        
        tokens = line.split()
        # print(tokens)
        
        #GETTING LOCATION 
        if tokens and tokens[0].strip(';') not in ['ORG' , 'END']:
            if tokens[0].endswith(","):
                if tokens[1] in ['DEC' , 'HEX']:
                    print("*"*50)
                    location.append(symbol_table[tokens[0].strip(',')])
                else :
                    continue
            else:
                if tokens[0] not in ['DEC' , 'HEX'] :
                    # location.append(symbol_table[tokens[0]])
                    location.append(symbol_table[tokens[0]])
    
        #Getting the Opcode and address 
        if tokens and tokens[0].strip(';') not in ['ORG' , 'END']:
            #Before it a Label 
            if tokens[0].endswith(","):
                if tokens[1] not in ['DEC' , 'HEX']:
                    if tokens[1] in MR_instruction_map.key() :
                        if tokens[-1] =='I':
                            opcode = get_binary_code(tokens[1] , 1)
                            if tokens[2]:
                                # if tokens[2] in symbol_table:
                                address = hex_to_binary(symbol_table[tokens[2]]) 
                                instruction.append(f'{opcode} {address}')
                        else :
                            opcode = get_binary_code(tokens[1] , 0)
                            address = hex_to_binary(symbol_table[tokens[2]]) 
                            instruction.append(f'{opcode} {address}')
                    
                    
                    elif tokens[1] in In_Out_instruction_map.keys():
                        instruction.append(bin(Register_instruction_map[tokens[0]])[2:].zfill(16))
                    
                    elif tokens[1] in In_Out_instruction_map.keys():
                        instruction.append(In_Out_instruction_map[tokens[1]])

                elif tokens[1] in ['DEC' , 'HEX']:
                    if tokens[1] == 'DEC':
                        if int(tokens[2]) >= 0 :
                            instruction.append(bin(int(tokens[2]))[2:].zfill(16))
                        else : 
                            x =int(tokens[2])* -1
                            x_b = bin(x)[2:].zfill(16)
                            n_value = twos_complement_xor(str(x_b))
                            instruction.append(n_value)
                            
                    else:
                        if tokens[2] :
                            x = bin(int(tokens[2], 16))[2:].zfill(16)
                            instruction.append(x)
                        
            # No Label 
            # Memory Refrence Instruction
            elif tokens[0] in MR_instruction_map.keys() :
                        if tokens[-1] =='I':
                            opcode = get_binary_code(tokens[0] , 1)
                            
                            # if tokens[2] in symbol_table:
                            address = hex_to_binary(symbol_table[tokens[1]]) 
                            instruction.append(f'{opcode} {address}')
                        else :
                            opcode = get_binary_code(tokens[0] , 0)
                            address = hex_to_binary(str(symbol_table[tokens[1]])) 
                            instruction.append(f'{opcode} {address}')
                                              
            #Register Refrence Instruction
            elif tokens[0] in Register_instruction_map.keys():
                # print("-"*30)
                # print(f'{symbol_table[tokens[0]]} : {bin(Register_instruction_map[tokens[0]])[2:].zfill(16)}')
                # instruction.append(bin(Register_instruction_map[tokens[0]])[2:].zfill(16))
                instruction.append(f"{hex_to_binary(str(Register_instruction_map[tokens[0]]))}")
                
                # print( instruction)
                
            #Input Output Instruction 
            elif tokens[0] in In_Out_instruction_map.keys():
                # print("-"*30)
                print(f'{symbol_table[tokens[0]]} : {In_Out_instruction_map[tokens[0]]}')
                instruction.append(In_Out_instruction_map[tokens[0]])
                
                
    for i in range(len(instruction)):
        print(f'{location[i]} : {instruction[i]}')
        

assembly_code_2 ="""
        ORG 100 /starting location
        CLE     / clear E
        CLA
        STA CTR
        LDA WRD
        SZA
        BUN ROT
        BUN STP
ROT,    CIL     /start rotating AC
        SZE
        BUN AGN
        BUN ROT
AGN,    CLE
        ISZ CTR
        SZA
        BUN ROT
STP,    HLT
        ORG 120
CTR,    HEX 0
WRD,    HEX 62C1
        END

"""
   
assembly_code_1 = """
            ORG 100
            LDA SUB
            CMA  
            INC  
            ADD  MIN
            STA  DIF
            HLT
MIN,        DEC  83
SUB,        DEC  -23 I
DIF,        HEX  0
            END;
"""



print(first_pass_assembler_sl(assembly_code_2))
second_pass_assembler(assembly_code_2)

