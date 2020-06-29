library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity motorController is
    generic(
    pwm_0_l : integer := 100000;
    pwm_0_r : integer := 100000;
    pwm_1_l : integer := 1000;
    pwm_1_r : integer := 100000;
    pwm_2_l : integer := 100000;
    pwm_2_r : integer := 1000
    );
	port(
	clk, rstn : in std_logic;
	action : in std_logic_vector(1 downto 0);
	en0, en1, input1, input2, input3, input4 : out std_logic
	);
end motorController;

architecture behavioral of motorController is
	signal pwm0, pwm1 : integer := 0;
	signal counter0, counter1 : integer := 0;
	signal pwm_width : integer := 100000;  -- 10KHz pwm signal for AXICLK
	signal enable : std_logic;
	
	begin

    process (clk)
	begin
	  if rising_edge(clk) then 
	    if rstn = '0' then
	        en0 <= '0';
	        en1 <= '0';
	    else
            counter0 <= counter0 + 1;
            counter1 <= counter1 + 1;
            if (counter0 < pwm0) then
                en0 <= '1';
            elsif (counter0 < pwm_width) then
                en0 <= '0';
            else
                counter0 <= 0;
            end if;
            
            if (counter1 < pwm1) then
                en1 <= '1';
            elsif (counter1 < pwm_width) then
                en1 <= '0';
            else
                counter1 <= 0;
            end if;
        end if;
      end if;
    end process;
    
    process(clk, rstn, action)
    begin
    if rising_edge(clk) then 
        if rstn = '0' then
            enable <= '0';
        else
            if action = "00" then
                enable <= '1';
                input1 <= '0';
                input2 <= '1';
                input3 <= '0';
                input4 <= '1';
                pwm0 <= pwm_0_l;
                pwm1 <= pwm_0_r;
            elsif action = "01" then  -- turn left
                enable <= '1';
                input1 <= '1';
                input2 <= '0';
                input3 <= '0';
                input4 <= '1';
                pwm0 <= pwm_1_l;
                pwm1 <= pwm_1_r;
            elsif action = "10" then  -- turn right
                enable <= '1';
                input1 <= '0';
                input2 <= '1';
                input3 <= '1';
                input4 <= '0';
                pwm0 <= pwm_2_l;
                pwm1 <= pwm_2_r;
            elsif action = "11" then  -- stop
                enable <= '0';
                input1 <= '0';
                input2 <= '0';
                input3 <= '0';
                input4 <= '0';
                pwm0 <= 1000;
                pwm1 <= 1000;
            end if;
        end if;
    end if;
    end process;

--	process(action)
--	begin
--	if action = "00" then
--		input1 <= '0';
--		input2 <= '1';
--		input3 <= '0';
--		input4 <= '1';
--		pwm0 <= pwm_0_l;
--		pwm1 <= pwm_0_r;
--	elsif action = "01" then  -- turn left
--		input1 <= '1';
--		input2 <= '0';
--		input3 <= '0';
--		input4 <= '1';
--		pwm0 <= pwm_1_l;
--		pwm1 <= pwm_1_r;
--	elsif action = "10" then  -- turn right
--		input1 <= '0';
--		input2 <= '1';
--		input3 <= '1';
--		input4 <= '0';
--		pwm0 <= pwm_2_l;
--		pwm1 <= pwm_2_r;
--	elsif action = "11" then  -- stop
--        input1 <= '0';
--        input2 <= '0';
--        input3 <= '0';
--        input4 <= '0';
--        pwm0 <= 1000;
--        pwm1 <= 1000;
--	end if;
--	end process;
	
--	process(clk)
--	begin
--	if rising_edge(clk) then
--        counter0 <= counter0 + 1;
--        counter1 <= counter1 + 1;
--        if (counter0 < pwm0) then
--            en0 <= '1';
--        elsif (counter0 < pwm_width) then
--            en0 <= '0';
--        else
--            counter0 <= 0;
--        end if;
        
--        if (counter1 < pwm1) then
--            en1 <= '1';
--        elsif (counter1 < pwm_width) then
--            en1 <= '0';
--        else
--            counter1 <= 0;
--        end if;
--    end if;
--	end process;

end behavioral;
